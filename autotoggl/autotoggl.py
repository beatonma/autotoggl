import logging
import os
import sqlite3
import time

import autotoggl.render

from datetime import timedelta

from autotoggl.config import Config
from autotoggl.toggl_api import TogglApiInterface, ApiError

BASE_DIR = os.path.expanduser('~/autotoggl/')
DB_NAME = os.path.join(BASE_DIR, 'toggl.db')
CONFIG_FILE = os.path.join(BASE_DIR, 'config.json')

# Special event name indicating that system status has changed
# Triggered by events such as user idle, system lock
EVENT_SYSTEM = '__SYS__'


def _init_logger(name=__file__, level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(logging.StreamHandler())
    return logger


logger = _init_logger()


class DbConnection:
    def __init__(self, filename=DB_NAME):
        if not os.path.exists(filename):
            raise Exception('Database does not exist yet.')
        self.conn = sqlite3.connect(filename)
        self.cursor = self.conn.cursor()
        self.alive = True

    def close(self, commit=True):
        if not self.alive:
            raise Exception(
                'Database connection has already been closed.')
        self.cursor.close()
        if commit:
            self.conn.commit()
        self.conn.close()
        self.alive = False

    def exec(self, *args):
        if not self.alive:
            raise Exception(
                'Cannot execute query: database connection '
                'has already been closed.')
        return self.cursor.execute(*args)

    def clean_up(self, consumed_only=True, older_than=timedelta(days=2)):
        pass

    def consume(self, events):
        '''
        Mark the given events (and any events merged with them) as consumed,
        meaning they have been submitted to Toggl successfully
        '''
        ids = [e.merged + [e.id] for e in events if e.consumed]
        sql = '''UPDATE toggl SET consumed=? WHERE rowid=?'''
        for rowid in ids:
            self.exec(sql, (True, rowid))


class Event:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.process = kwargs.get('process')
        self.title = kwargs.get('title')
        self.start = kwargs.get('start')
        self.consumed = kwargs.get('consumed', False)
        self.project = kwargs.get('project')

        self.duration = kwargs.get('duration', 0)

        self.merged = []

    def merge(self, other):
        self.duration += other.duration
        other.duration = 0
        self.merged.append(other.id)


def load_config():
    return Config(CONFIG_FILE)


def get_events_for_date(db, date, day_ends_at=3):
    date_starts = date.replace(
        hour=day_ends_at, minute=0, second=0, microsecond=0)
    date_ends = date_starts + timedelta(days=1)
    logger.info(
        'Getting events between {} and {}'.format(date_starts, date_ends))

    date_starts = date_starts.timestamp()
    date_ends = date_ends.timestamp()

    c = db.exec('''SELECT rowid, process_name, window_title, start, consumed
                   FROM toggl
                   WHERE start>=? AND start<=?''',
                (date_starts, date_ends))
    return [
        Event(
            id=r[0],
            process=r[1],
            title=r[2],
            start=r[3],
            consumed=bool(r[4]),
        ) for r in c.fetchall()]


def categorise_event(event, definitions):
    '''
    If we recognise the window title, try to parse a project name from it
    '''
    process = event.process
    title = event.title

    process_classifier = definitions.get(process, None)
    if process_classifier:
        project = process_classifier.get_project(title)
        event.description = process_classifier.get_description(title)

        if project:
            event.project = project
            return project

    return None


def categorise_events(events, definitions):
    '''
    Build a dictionary of projects
    {
        project_name: [events_list,]
    }
    '''
    projects = {}
    for x in events:
        project = categorise_event(x, definitions)
        if not project:
            continue

        if project in projects:
            projects[project].append(x)
        else:
            projects[project] = [x]

    # Remove events that are not assigned to any projects
    events = list(filter(lambda x: x.project, events))

    return events, projects


def compress_events(events, config):
    '''
    Remove events that are very short and squash the results.
    If two events in series represent the same activity, the duration
    properties of the second event will be added to the first event
    and the second event will be removed from the events list
    TODO smarter handling of system events: pause/resume events
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

        for o in events[n+1:]:
            if o.title == EVENT_SYSTEM:
                o.duration = 0
                break

            if o.duration < config.minimum_event_seconds:
                e.merge(o)
            elif e.title == o.title:
                # If consecutive events have the same name then
                # squash them into the first occurrence
                e.merge(o)
            else:
                # Another event long enough to take over
                break

    # Remove any event with 0 duration
    return list(filter(lambda x: x.duration, events))


def submit(interface, projects):
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
                    e.start,
                    e.duration,)
                e.consumed = True
                successful.append(e)
            except ApiError as err:
                failed.append(e)
                logger.warn(err)
            time.sleep(1)

    return successful, failed


def main():
    db = DbConnection()
    config = load_config()

    events = get_events_for_date(db, config.date, config.day_ends_at)
    events = compress_events(events, config)

    events, projects = categorise_events(events, config.project_definitions)

    if not events:
        logger.info('No events!')
        raise SystemExit()

    if config.render:
        logger.info('Building preview HTML...')
        autotoggl.render.render_events(events)

    if not config.local:
        api = TogglApiInterface(config)
        successful, failed = submit(api, projects)

        db.consume(successful)

        if failed:
            logger.warn('{} events failed to be submitted'.format(len(failed)))

    db.close()


if __name__ == '__main__':
    main()
