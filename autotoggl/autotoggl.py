import datetime
import json
import logging
import os
import sqlite3
import time

import autotoggl.render

from datetime import timedelta
from typing import Dict, List, Tuple

from autotoggl.config import Config
from autotoggl.api import TogglApiInterface, ApiError
from autotoggl.util import midnight

BASE_DIR = os.path.expanduser('~/autotoggl/')
DB_PATH = os.path.join(BASE_DIR, 'toggl.db')
CONFIG_FILE = os.path.join(BASE_DIR, 'config.json')

# Special event name indicating that system status has changed
# Triggered by events such as user idle, system lock
EVENT_SYSTEM = '__SYS__'


def _init_logger(name=__file__, level=logging.DEBUG) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(logging.StreamHandler())
    return logger


logger = _init_logger()


class Event:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.process = kwargs.get('process')
        self.title = kwargs.get('title')
        self.start = kwargs.get('start')
        self.consumed = kwargs.get('consumed', False)
        self.project = kwargs.get('project')
        self.tags = kwargs.get('tags', [])
        self.description = kwargs.get('description')

        self.duration = kwargs.get('duration', 0)

        self.merged = []

    def merge(self, other) -> None:
        self.duration += other.duration
        other.duration = 0
        self.merged.append(other.id)

    def __repr__(self):
        return json.dumps(self.__dict__, indent=2, sort_keys=True)


class DatabaseManager:
    def __init__(self, filename=DB_PATH):
        if not os.path.exists(filename):
            self._create(filename)
        self.conn = sqlite3.connect(filename)
        self.cursor = self.conn.cursor()
        self.alive = True

    def __enter__(self):
        return self

    def __exit__(self, ctx_type, ctx_value, ctx_traceback):
        self.close(commit=True)

    def _create(self, filename) -> None:
        logger.info('Creating database {}'.format(filename))
        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        conn = sqlite3.connect(filename)
        cursor = conn.cursor()

        sql = '''CREATE TABLE toggl
                 (process_name TEXT NOT NULL,
                  window_title TEXT NOT NULL,
                  start INTEGER NOT NULL,
                  consumed BOOLEAN NOT NULL DEFAULT 0)'''
        cursor.execute(sql)
        cursor.close()
        conn.commit()
        conn.close()

    def close(self, commit=True) -> None:
        if not self.alive:
            raise Exception(
                'Database connection has already been closed.')
        self.cursor.close()
        if commit:
            self.conn.commit()
        self.conn.close()
        self.alive = False

    def exec(self, *args) -> sqlite3.Cursor:
        if not self.alive:
            raise Exception(
                'Cannot execute query: database connection '
                'has already been closed.')
        try:
            return self.cursor.execute(*args)
        except Exception as e:
            logger.error(
                'Unable to execute query {args}: {err}'
                .format(args=args, err=e))

    def clean_up(self, **kwargs) -> None:
        clear_all = kwargs.get('all', False)
        older_than_days = kwargs.get('older_than', 2)
        before = kwargs.get('before')

        if not before:
            before = midnight(datetime.datetime.now()
                              - timedelta(days=older_than_days))

        logger.warn('Removing events before {}'.format(before.isoformat()))
        before_timestamp = before.timestamp()
        if clear_all:
            sql = '''DELETE FROM toggl
                     WHERE start<?'''
            self.exec(sql, (before_timestamp,))
        else:
            sql = '''DELETE FROM toggl
                     WHERE start<? AND consumed=?'''
            self.exec(sql, (before_timestamp, True))

        changes = self.exec('''SELECT changes()''').fetchone()[0]

        self.exec('''VACUUM''')  # Free up space
        logger.info('Deleted {} events'.format(changes))

    def consume(self, events) -> None:
        '''
        Mark the given events (and any events merged with them) as consumed,
        meaning they have been submitted to Toggl successfully
        '''
        ids = []
        for e in events:
            if e.consumed:
                ids += e.merged
                ids.append(e.id)
        sql = '''UPDATE toggl SET consumed=? WHERE rowid=?'''
        for rowid in ids:
            self.exec(sql, (True, rowid))

    def get_events(self, start_datetime, end_datetime) -> List[Event]:
        c = self.exec(
            '''SELECT rowid, process_name, window_title, start, consumed
               FROM toggl
               WHERE start>=? AND start<=?''',
            (start_datetime.timestamp(), end_datetime.timestamp()))
        return [
            Event(
                id=r[0],
                process=r[1],
                title=r[2],
                start=r[3],
                consumed=bool(r[4]),
            ) for r in c.fetchall()]

    def reset(self, start_datetime, end_datetime) -> None:
        sql = '''UPDATE toggl
                 SET consumed=?
                 WHERE start>=? AND start<=?'''
        self.exec(
            sql,
            (False, start_datetime.timestamp(), end_datetime.timestamp()))


def load_config() -> Config:
    return Config(CONFIG_FILE)


def get_events_for_date(db, date, day_ends_at=3) -> List[Event]:
    date_starts = date.replace(
        hour=day_ends_at, minute=0, second=0, microsecond=0)
    date_ends = date_starts + timedelta(days=1)
    logger.info(
        'Getting events between {} and {}'.format(date_starts, date_ends))

    return db.get_events(date_starts, date_ends)


def categorise_event(event, definitions) -> str:
    '''
    If we recognise the window title, try to parse a project name from it
    '''
    process = event.process
    title = event.title

    process_classifier = definitions.get(process, None)
    if process_classifier:
        result = process_classifier.get(title)
        if result:
            event.project = result.project
            event.description = result.description
            event.tags = result.tags
            return result.project

    return None


def categorise_events(events, definitions) -> None:
    for e in events:
        categorise_event(e, definitions)


def build_project_dict(events) -> Dict[str, Event]:
    projects = {}
    for e in events:
        if not e.project:
            continue

        if e.project in projects:
            projects[e.project].append(e)
        else:
            projects[e.project] = [e]

    return projects


def compress_events(events, config) -> List[Event]:
    '''
    'Squash' the events list into as few event objects as possible..

    Squashing the results means:
        - If an event is very short, merge it with the ongoing event. If
          there is no ongoing event then ignore it.

        - If two events in series represent the same activity, the duration
          properties of the second event will be added to the first event
          and the second event will be removed from the events list

        - Any events that are not assigned to a project will be merged
          into any ongoing event. If there is no event ongoing, unassigned
          events will be ignored.
    '''
    # Ensure events are in order of occurrence
    events.sort(key=lambda x: x.start)

    # Calculate naive durations by going through the events pairwise
    for a, b in zip(events[:-1], events[1:]):
        a.duration = b.start - a.start

    # Calculate complete durations by weeding out short events
    # and taking system events into account
    for n, e in enumerate(events):
        if (e.duration < config.minimum_event_seconds
                or e.title == EVENT_SYSTEM):
            e.duration = 0
            continue

        if not e.project:
            # Unassigned events should be ignored at this stage
            continue

        for o in events[n+1:]:
            if o.title == EVENT_SYSTEM:
                # o.duration = 0
                break

            if o.duration < config.minimum_event_seconds:
                e.merge(o)

            elif e.title == o.title:
                # If consecutive events have the same name then
                # squash them into the first occurrence
                e.merge(o)

            elif not o.project:
                # Merge unassigned events into the ongoing event
                e.merge(o)

            else:
                # Another event long enough to take over
                break

    # Remove any event with 0 duration
    # or no project assignment
    return list(filter(lambda x: x.duration and x.project, events))


def get_total_duration(events) -> int:
    return sum([e.duration for e in events])


def print_events(events, starts, ends) -> None:
    logger.info(
        'Events from {} -> {}'
        .format(starts.isoformat(), ends.isoformat()))
    for e in events:
        logger.info(e)


def submit(interface, projects) -> Tuple[List[int], List[int]]:
    interface.get_all_projects()
    successful = []
    failed = []
    for p, events in projects.items():
        if p not in interface.projects:
            logger.debug('Creating project \'{}\''.format(p))
            try:
                interface.create_project(p)
            except ApiError as e:
                logger.warn(e)

        for e in events:
            if e.consumed:
                continue

            try:
                interface.create_time_entry(
                    e.project,
                    e.description,
                    e.start,
                    e.duration,
                    tags=e.tags)
                e.consumed = True
                successful.append(e)
            except ApiError as err:
                failed.append(e)
                logger.warn(err)
            time.sleep(1)

    return successful, failed


def main() -> None:
    with DatabaseManager() as db:
        config = load_config()

        if config.config:
            os.startfile(os.path.normpath(CONFIG_FILE))
            return

        if config.clean:
            db.clean_up(**config.clean)
            return

        if config.reset:
            db.reset(config.day_starts, config.day_ends)
            logger.info(
                'All entries between {} and {} have been reset'
                .format(
                    config.day_starts.isoformat(),
                    config.day_ends.isoformat()))
            return

        events = get_events_for_date(db, config.date, config.day_ends_at)
        categorise_events(
            events, config.classifiers)
        events = compress_events(events, config)
        projects = build_project_dict(events)

        if config.showall:
            print_events(
                events, config.day_starts, config.day_ends)

        if not events:
            logger.info('No events!')
            raise SystemExit()

        if config.render:
            logger.info('Building preview HTML...')
            autotoggl.render.render_events(events)

        pending_submission = 0
        for p in projects:
            n_total_events = len(projects[p])
            projects[p] = [e for e in projects[p] if not e.consumed]
            n_pending_events = len(projects[p])
            logger.info(
                'Project \'{project}\': [{duration}] {pending} events '
                '({consumed} already consumed)'
                .format(
                    project=p,
                    duration=timedelta(seconds=get_total_duration(projects[p])),
                    pending=n_pending_events,
                    consumed=n_total_events - n_pending_events))
            pending_submission += n_pending_events

        if pending_submission > 0 and not config.local:
            api = TogglApiInterface(config)
            successful, failed = submit(api, projects)

            db.consume(successful)

            if failed:
                logger.warn(
                    '{} events failed to be submitted'.format(len(failed)))


if __name__ == '__main__':
    main()
