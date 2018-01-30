import json
import logging
import os
import re
import requests
import sqlite3

from datetime import datetime, timedelta

DB_NAME = os.path.expanduser('~/toggl.db')

# Special event name indicating that system status has changed
# Triggered by events such as user idle, system lock
EVENT_SYSTEM = '__SYS__'

# 3am - Use this time as 'midnight'.
# Any events recorded between midnight and this hour will be grouped
# with the date of the previous calendar day
DAY_ENDS_AT = 3

MINIMUM_EVENT_LENGTH_SECONDS = 60



def _init_logger(name=__file__, level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(logging.StreamHandler())
    return logger

logger = _init_logger()


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

    def clean_up(older_than=timedelta(days=2)):
        pass


def get_events_for_date(db, date):
    date_starts = date.replace(
        hour=DAY_ENDS_AT, minute=0, second=0, microsecond=0)
    date_ends = date_starts + timedelta(days=1)
    logger.info(
        'Getting events between {} and {}'.format(date_starts, date_ends))

    date_starts = date_starts.timestamp()
    date_ends = date_ends.timestamp()

    c = db.exec('''SELECT process_name, window_title, timestamp FROM toggl
                   WHERE timestamp>=? AND timestamp<=?''',
                (date_starts, date_ends))
    return [
        {
            'process': r[0],
            'title': r[1],
            'timestamp': r[2],
            'duration': 0,
        } for r in c.fetchall()]


def categorise_event(event):
    '''
    If we recognise the window title, try to parse a project name from it
    '''
    process = event.get('process')
    title = event.get('title')
    timestamp = event.get('timestamp')
    project = None

    if process == 'sublime_text':
        # e.g. ../auto-toggl/main.py (auto-toggl) - Sublime Text
        m = re.match(r'.*\((.*?)\) - Sublime Text.*', title)
        if m:
            project = m.group(1)
        else:
            logger.warn('Sublime Text pattern failed: {}'.format(title))

    elif process == 'studio64':
        m = re.match(r'(.*?) - \[.*\].*', title)
        if m:
            project = m.group(1)
        else:
            logger.warn('Android Studio pattern failed: {}'.format(title))

    elif process == 'chrome':
        if 'Duolingo' in title:
            project = 'Duolingo'
        elif [x
              for x in ['reddit', 'politics', 'starcraft', 'news', 'guardian']
              if x in title.lower()]:
            project = 'Passive'

    return project


def categorise_events(events):
    '''
    Build a dictionary of projects 
    {
        project_name: [events_list,]
    }
    '''
    projects = {}
    for x in events:
        project = categorise_event(x)
        if not project:
            continue

        if project in projects:
            projects[project].append(x)
        else:
            projects[project] = [x]
    return projects


def compress_events(events):
    '''
    Remove any events that are too short. Not sure this is a useful thing to do
    '''
    compressed = []

    # Go through event pairs (n, n+1)
    for a, b in zip(events[:-1], events[1:]):
        # print(a, b)
        length = b['timestamp'] - a['timestamp']
        if length >= MINIMUM_EVENT_LENGTH_SECONDS:
            compressed.append(a)
        else:
            print(
                'Skipping event {} with length={} seconds'
                .format(a['process'], length))
    return compressed


def calculate_event_durations(events):
    # events_with_duration = []

    # Ensure events are in order of occurrence
    events.sort(key=lambda x: x['timestamp'])

    for a, b in zip(events[:-1], events[1:]):
        a['duration'] = b['timestamp'] - a['timestamp']

    for x in events:
        print(x)

    for n, e in enumerate(events):
        print(n)
        if e['duration'] < MINIMUM_EVENT_LENGTH_SECONDS:
            e['duration'] = 0
            continue

        for o in events[n+1:]:
            # print(e['process'], e['timestamp'], o['timestamp'], o['process'])
            if o['title'] == EVENT_SYSTEM:
                o['duration'] = 0
                break
            if o['duration'] < MINIMUM_EVENT_LENGTH_SECONDS:
                logger.debug(
                    'Extending event by {} seconds'.format(o['duration']))
                e['duration'] += o['duration']
                o['duration'] = 0
                # continue
            # logger.debug('Event not altered by following events')




        # if event['title'] == EVENT_SYSTEM:
        #     duration = 
        # else:
        #     duration = 

        # logger.debug('{}: \'{}\''.format(n, e))




if __name__ == '__main__':
    db = DbConnection()
    events_today = get_events_for_date(db, datetime.today())
    events_today = compress_events(events_today)

    if not events_today:
        logger.debug('No events')
        raise SystemExit()

    projects = {}
    for x in events_today:
        project = categorise_event(x)
        if not project:
            continue

        if project in projects:
            projects[project].append(x)
        else:
            projects[project] = [x]


    logger.info('Today:')
    for key, value in projects.items():
        logger.info('  {}: {}'.format(key, len(value)))

    logger.info('{} projects'.format(len(projects)))
