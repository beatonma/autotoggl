import json
import logging
import os
import re
import sqlite3
import time

from argparse import ArgumentParser
from datetime import datetime, timedelta

from toggl_api import TogglApiInterface, ApiError

BASE_DIR = os.path.expanduser('~/autotoggl/')
DB_NAME = os.path.join(BASE_DIR, 'toggl.db')
CONFIG_FILE = os.path.join(BASE_DIR, 'config.json')

# Special event name indicating that system status has changed
# Triggered by events such as user idle, system lock
EVENT_SYSTEM = '__SYS__'

# 3am - Use this time as 'midnight'.
# Any events recorded between midnight and this hour will be grouped
# with the date of the previous calendar day
DAY_ENDS_AT = 3

DEFAULT_DAY = datetime.today() - timedelta(days=1)  # yesterday

MINIMUM_EVENT_LENGTH_SECONDS = 60


def _init_logger(name=__file__, level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(logging.StreamHandler())
    return logger


logger = _init_logger()


def _parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        'day',
        choices=[
            'today',
            'yesterday',
        ],
        default='yesterday',
        nargs='?'
    )
    parser.add_argument(
        '--date',
        type=str,
        default=None,
        help='(yy)yy-mm-dd format'
    )

    args = parser.parse_args()
    if args.date:
        m = re.match(r'(\d{2})?(\d{2})-(\d{2})-(\d{2})', args.date)
        if m:
            args.date = datetime(
                year=int('{}{}'.format(m.group(1) or '20', m.group(2))),
                month=int(m.group(3)),
                day=int(m.group(4)))
    else:
        if args.day == 'today':
            args.date = datetime.today()
        elif args.day == 'yesterday':
            args.date = datetime.today() - timedelta(days=1)

    return args


class DbConnection:
    def __init__(self, filename=DB_NAME):
        if not os.path.exists(filename):
            raise Exception('Database does not exist yet')
        self.conn = sqlite3.connect(filename)
        self.cursor = self.conn.cursor()
        self.alive = True

    def close(self, commit=True):
        if not self.alive:
            raise Exception(
                'Database connection has already been closed')
        self.cursor.close()
        if commit:
            self.conn.commit()
        self.conn.close()
        self.alive = False

    def exec(self, *args):
        return self.cursor.execute(*args)

    def clean_up(consumed_only=True, older_than=timedelta(days=2)):
        pass


class ProcessClassifier:
    def __init__(self, json_data=None):
        if json:
            self._from_json(json_data)
        else:
            self.process = ''

    def _from_json(self, j):
        self.process = j.get('process')
        self.project_pattern = j.get('project_pattern')
        self.projects = j.get('projects')

    def get_project(self, window_title):
        project = None

        if self.project_pattern:
            m = re.match(self.project_pattern, window_title)
            if m:
                project = m.group(1)
                return project
        if self.projects:
            for p in self.projects:
                if [x for x in p.get('window_contains')
                        if x in window_title.lower()]:
                    return p.get('title')

    def __repr__(self):
        return json.dumps({
                'process': self.process,
                'project_pattern': self.project_pattern,
                'projects': self.projects,
            }, indent=2)


def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}

    config = None

    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)

    if not config:
        return {}

    defs = {}
    for x in config.get('project_definitions', []):
        defs[x['process']] = ProcessClassifier(x)

    del config['project_definitions']

    if 'api_key' not in config:
        logger.warn('API key is not configured')
    if not defs:
        logger.warn('No project definitions are configured')

    return config, defs


def get_events_for_date(db, date):
    date_starts = date.replace(
        hour=DAY_ENDS_AT, minute=0, second=0, microsecond=0)
    date_ends = date_starts + timedelta(days=1)
    logger.info(
        'Getting events between {} and {}'.format(date_starts, date_ends))

    date_starts = date_starts.timestamp()
    date_ends = date_ends.timestamp()

    c = db.exec('''SELECT process_name, window_title, start, consumed, rowid
                   FROM toggl
                   WHERE start>=? AND start<=?''',
                (date_starts, date_ends))
    return [
        {
            'process': r[0],
            'title': r[1],
            'start': r[2],
            'consumed': bool(r[3]),
            'duration': 0,
            'id': r[4]
        } for r in c.fetchall()]


def categorise_event(event, definitions):
    '''
    If we recognise the window title, try to parse a project name from it
    '''
    process = event.get('process')
    title = event.get('title')

    if definitions:
        process_classifier = definitions.get(process, None)
        if process_classifier:
            project = process_classifier.get_project(title)
            if project:
                event['project'] = project
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
        project = categorise_event(x, project_definitions)
        if not project:
            continue

        if project in projects:
            projects[project].append(x)
        else:
            projects[project] = [x]

    # Remove events that are not assigned to any projects
    events = list(filter(lambda x: 'project' in x, events))

    return events, projects


def calculate_event_durations(events):
    '''
    Remove events that are very short.
    '''
    # Ensure events are in order of occurrence
    events.sort(key=lambda x: x['start'])

    # Calculate naive durations by going through the events pairwise
    for a, b in zip(events[:-1], events[1:]):
        a['duration'] = b['start'] - a['start']

    # Calculate complete durations by weeding out short events
    # and taking system events into account
    for n, e in enumerate(events):
        if (e['duration'] < MINIMUM_EVENT_LENGTH_SECONDS
                or e['title'] == EVENT_SYSTEM):
            e['duration'] = 0
            continue

        for o in events[n+1:]:
            if o['title'] == EVENT_SYSTEM:
                o['duration'] = 0
                break

            if o['duration'] < MINIMUM_EVENT_LENGTH_SECONDS:
                e['duration'] += o['duration']
                o['duration'] = 0
            elif e['title'] == o['title']:
                # If consecutive events have the same name then
                # squash them into the first occurrence
                e['duration'] += o['duration']
                o['duration'] = 0
            else:
                # Another event long enough to take over
                break

    # Remove any event with 0 duration
    return list(filter(lambda x: x['duration'], events))


def submit(interface, projects, db):
    interface.get_all_projects()
    for p, events in projects.items():
        if p not in interface.projects:
            logger.debug('Creating project \'{}\''.format(p))
            try:
                interface.create_project(p)
            except ApiError as e:
                logger.warn(e)

        consumed = []

        for e in events:
            if e['consumed']:
                continue

            try:
                interface.create_time_entry(
                    e['project'],
                    e['start'],
                    e['duration'],)
                e['consumed'] = True
                consumed.append(e)
            except ApiError as e:
                logger.warn(e)
            time.sleep(1)

        consume(db, consumed)


def consume(db, events):
    '''
    mark events as consumed once they have been submitted successfully
    '''

    n = 0
    for e in events:
        if e['consumed']:
            sql = '''
            UPDATE toggl SET consumed=? WHERE rowid=?
            '''
            db.exec(sql, (True, e['id'],))
            n += 1
    logger.debug('Consumed {} events'.format(n))


if __name__ == '__main__':
    args = _parse_args()
    db = DbConnection()
    config, project_definitions = load_config()

    events = get_events_for_date(db, args.date)
    events = calculate_event_durations(events)

    events, projects = categorise_events(events, project_definitions)

    if not events:
        logger.debug('No events')
        raise SystemExit()

    # logger.info('Today:')
    # for key, value in projects.items():
    #     logger.info('  {}: {}'.format(key, len(value)))

    logger.info(json.dumps(projects, indent=2))

    logger.info('{} projects'.format(len(projects)))

    api = TogglApiInterface(config)
    submit(api, projects, db)

    db.close()
