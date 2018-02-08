import datetime
import os
import random

from datetime import timedelta

import autotoggl.autotoggl as autotoggl

from autotoggl.config import Config
from autotoggl.util import midnight

from autotoggl.render import render_events

from tests import test_common
from tests.test_common import equal
from tests.test_credentials import (
    TEST_WORKSPACE,
    TEST_WORKSPACE_ID,
    TEST_API_KEY,
)


logger = test_common.get_logger(__name__)
autotoggl.logger = logger
autotoggl.BASE_DIR = os.path.expanduser('~/autotoggl/test/')
autotoggl.DB_PATH = os.path.join(autotoggl.BASE_DIR, 'toggl.db')


class Bunch(object):
    '''Dictionary wrapper'''
    def __init__(self, adict):
        self.__dict__.update(adict)


EVENTS = [
    {'duration': 0, 'title': 'StarCraft on Reddit', 'process': 'chrome', 'start': datetime.datetime(2018, 1, 30, 10, 22).timestamp()},
    {'duration': 0, 'title': 'Commons - [/path/to/project] - FileName.java - Android Studio 3.0.1', 'process': 'studio64', 'start': datetime.datetime(2018, 1, 30, 10, 23, 30).timestamp()},
    {'duration': 0, 'title': '/gdbackup/gdbackup.py (gdbackup) - Sublime Text', 'process': 'sublime_text', 'start': datetime.datetime(2018, 1, 30, 10, 23, 50).timestamp()},
    {'duration': 0, 'title': '__SYS__', 'process': 'System.Idle', 'start': datetime.datetime(2018, 1, 30, 10, 24, 35).timestamp()},
    {'duration': 0, 'title': 'LEDControl - [/path/to/project] - FileName.java - Android Studio 3.0.1', 'process': 'studio64', 'start': datetime.datetime(2018, 1, 30, 10, 25, 5).timestamp()},
    {'duration': 0, 'title': 'StarCraft on Reddit', 'process': 'chrome', 'start': datetime.datetime(2018, 1, 30, 11, 55, 5).timestamp()},
    {'duration': 0, 'title': 'CommonsManager - [/path/to/project] - FileName.java - Android Studio 3.0.1', 'process': 'studio64', 'start': datetime.datetime(2018, 1, 30, 11, 55, 25).timestamp()},
    {'duration': 0, 'title': 'StarCraft on Reddit', 'process': 'chrome', 'start': datetime.datetime(2018, 1, 30, 11, 56, 10).timestamp()},
    {'duration': 0, 'title': '/gdbackup/gdbackup.py (gdbackup) - Sublime Text', 'process': 'sublime_text', 'start': datetime.datetime(2018, 1, 30, 11, 56, 55).timestamp()},
    {'duration': 0, 'title': '/gdbackup/gdbackup.py (gdbackup) - Sublime Text', 'process': 'sublime_text', 'start': datetime.datetime(2018, 1, 30, 11, 58, 25).timestamp()},
    {'duration': 0, 'title': '__SYS__', 'process': 'System.SessionLock', 'start': datetime.datetime(2018, 1, 30, 12, 28, 25).timestamp()},
    {'duration': 0, 'title': '__SYS__', 'process': 'System.SessionUnlock', 'start': datetime.datetime(2018, 1, 30, 12, 28, 55).timestamp()},
    {'duration': 0, 'title': 'Commons - [/path/to/project] - FileName.java - Android Studio 3.0.1', 'process': 'studio64', 'start': datetime.datetime(2018, 1, 30, 12, 30, 55).timestamp()},
    {'duration': 0, 'title': 'Commons - [/path/to/project] - FileName.java - Android Studio 3.0.1', 'process': 'studio64', 'start': datetime.datetime(2018, 1, 30, 14, 0, 55).timestamp()},
    {'duration': 0, 'title': 'LEDControl - [/path/to/project] - FileName.java - Android Studio 3.0.1', 'process': 'studio64', 'start': datetime.datetime(2018, 1, 30, 14, 1).timestamp()},
    {'duration': 0, 'title': 'LEDControl - [/path/to/project] - FileName.java - Android Studio 3.0.1', 'process': 'studio64', 'start': datetime.datetime(2018, 1, 30, 14, 1, 5).timestamp()},
    {'duration': 0, 'title': '/gdbackup/gdbackup.py (gdbackup) - Sublime Text', 'process': 'sublime_text', 'start': datetime.datetime(2018, 1, 30, 14, 3, 5).timestamp()},
    {'duration': 0, 'title': '__SYS__', 'process': 'System.UnIdle', 'start': datetime.datetime(2018, 1, 30, 14, 3, 10).timestamp()},
    {'duration': 0, 'title': 'CommonsManager - [/path/to/project] - FileName.java - Android Studio 3.0.1', 'process': 'studio64', 'start': datetime.datetime(2018, 1, 30, 14, 3, 15).timestamp()},
    {'duration': 0, 'title': '/auto-toggl/main.py (auto-toggl) - Sublime Text', 'process': 'sublime_text', 'start': datetime.datetime(2018, 1, 30, 14, 3, 45).timestamp()},
    {'duration': 0, 'title': '/gdbackup/gdbackup.py (gdbackup) - Sublime Text', 'process': 'sublime_text', 'start': datetime.datetime(2018, 1, 30, 14, 4, 30).timestamp()},
    {'duration': 0, 'title': 'LEDControl - [/path/to/project] - FileName.java - Android Studio 3.0.1', 'process': 'studio64', 'start': datetime.datetime(2018, 1, 30, 14, 6).timestamp()},
    {'duration': 0, 'title': '__SYS__', 'process': 'System.UnIdle', 'start': datetime.datetime(2018, 1, 30, 14, 6, 5).timestamp()},
    {'duration': 0, 'title': 'Politics', 'process': 'chrome', 'start': datetime.datetime(2018, 1, 30, 15, 36, 5).timestamp()},
    {'duration': 0, 'title': 'LEDControl - [/path/to/project] - FileName.java - Android Studio 3.0.1', 'process': 'studio64', 'start': datetime.datetime(2018, 1, 30, 15, 38, 5).timestamp()},
]


def generate_events(howmany=15):
    EVENT_TYPES = [
        ('sublime_text', '/auto-toggl/main.py (auto-toggl) - Sublime Text'),
        ('sublime_text', '/gdbackup/gdbackup.py (gdbackup) - Sublime Text'),
        ('studio64', 'LEDControl - [/path/to/project] - FileName.java - Android Studio 3.0.1'),
        ('studio64', 'Commons - [/path/to/project] - FileName.java - Android Studio 3.0.1'),
        ('studio64', 'CommonsManager - [/path/to/project] - FileName.java - Android Studio 3.0.1'),
        ('chrome', 'reddit: the front page of the internet'),
        ('chrome', 'Politics'),
        ('chrome', 'StarCraft on Reddit'),
        ('System.SessionLock', '__SYS__'),
        ('System.SessionUnlock', '__SYS__'),
        ('System.Idle', '__SYS__'),
        ('System.UnIdle', '__SYS__'),
    ]
    EVENT_LENGTHS = [
        2,
        5,
        20,
        30,
        45,
        90,
        60 * 2,
        60 * 30,
        60 * 90,
    ]

    time = datetime.datetime.today().replace(hour=9, second=0, microsecond=0)
    events = []
    for x in range(0, howmany):
        time = time + timedelta(seconds=random.choice(EVENT_LENGTHS))
        e = random.choice(EVENT_TYPES)
        events.append(
            {
                'process': e[0],
                'title': e[1],
                'start': time,
                'duration': 0,
            }
        )

    for x in events:
        print('{},'.format(x))
    return events


def test_compress_events(events=None, config=None):
    if not config:
        config = test_common.get_test_config()
    if not events:
        events = [autotoggl.Event(**x) for x in EVENTS]

    events = autotoggl.compress_events(events, config)
    for e in events:
        autotoggl.categorise_event(e, config.defs())

    EXPECTED_VALUES = [
        {'duration': 155, 'title': 'StarCraft on Reddit', 'process': 'chrome', 'start': '10:22:00'},
        {'duration': 5510, 'title': 'LEDControl - [/path/to/project] - FileName.java - Android Studio 3.0.1', 'process': 'studio64', 'start': '10:25:05'},
        {'duration': 1890, 'title': '/gdbackup/gdbackup.py (gdbackup) - Sublime Text', 'process': 'sublime_text', 'start': '11:56:55'},
        {'duration': 5410, 'title': 'Commons - [/path/to/project] - FileName.java - Android Studio 3.0.1', 'process': 'studio64', 'start': '12:30:55'},
        {'duration': 125, 'title': 'LEDControl - [/path/to/project] - FileName.java - Android Studio 3.0.1', 'process': 'studio64', 'start': '14:01:05'},
        {'duration': 95, 'title': '/gdbackup/gdbackup.py (gdbackup) - Sublime Text', 'process': 'sublime_text', 'start': '14:04:30'},
        {'duration': 120, 'title': 'Politics', 'process': 'chrome', 'start': '15:36:05'},
    ]

    equal(len(events), len(EXPECTED_VALUES), data=events)

    for x, y in zip(events, EXPECTED_VALUES):
        equal(int(x.duration), int(y['duration']), data=[x, y])
        equal(x.process, y['process'], data=[x, y])
        equal(x.title, y['title'], data=[x, y])

    render_events(events)


def test_categorise_event():
    '''
    Confirm that categorise_event returns the correct project name,
    and correctly updates the given Event object
    '''
    config = test_common.get_test_config()

    # Test basic project name via window_contains
    equal(
        autotoggl.categorise_event(
            autotoggl.Event(title='Duolingo', process='chrome'),
            config.defs()),
        'Duolingo')

    # Test basic project name via pattern-matching
    equal(
        autotoggl.categorise_event(
            autotoggl.Event(
                title='/auto-toggl/main.py (auto-toggl) - Sublime Text',
                process='sublime_text'),
            config.defs()),
        'auto-toggl')

    # Test that categorise_event correctly updates the original Event object
    event = autotoggl.Event(
        title='LEDControl - [/path/to/proj] - File.java - Android Studio 3.0',
        process='studio64')
    autotoggl.categorise_event(event, config.defs())
    equal(event.project, 'LEDControl')
    equal(event.description, 'File.java')
    equal(event.tags, ['android', 'dev'])


def test_project_definitions():
    '''
    Confirm that Classifier.get() constructs the correct result
    '''
    config = test_common.get_test_config()
    classifiers = config.classifiers

    # Window titles
    sublimetext = '../auto-toggl/autotoggl.py (auto-toggl) - Sublime Text'
    sublimetext_with_alias = '../../settings.py (gassistant) - Sublime Text'
    studio64 = 'ProjectName - [/path/to/proj] - File.java - Android Studio 3.0'
    chrome_reddit = 'reddit: the front page of the internet'
    chrome_iplayer = 'BBC iPlayer - Requiem - Series 1: Episode 1'
    chrome_netflix = 'Netflix'

    # Project and description are parsed using regex patterns
    result = classifiers['sublime_text'].get(sublimetext)
    equal(result.project, 'auto-toggl')
    equal(result.description, 'autotoggl.py')
    equal(result.tags, [])

    # As above, but replace project name with an alias
    result = classifiers['sublime_text'].get(sublimetext_with_alias)
    equal(result.project, 'Home Assistant')  # 'gassistant' -> 'Home Assistant'
    equal(result.description, 'settings.py')
    equal(result.tags, [])

    # Project and description are parsed using regex patterns
    result = classifiers['studio64'].get(studio64)
    equal(result.project, 'ProjectName')
    equal(result.description, 'File.java')
    equal(result.tags, ['android', 'dev'])

    ###

    # Chrome process uses 'projects' list of subclassifiers and
    # primarily uses 'window_contains' to match windows with projects

    result = classifiers['chrome'].get(chrome_reddit)

    # Static project name found using window_contains
    equal(result.project, 'Casual')

    # Static description found using window_contains
    equal(result.description, 'Internetting')

    # Combines tags from both parent and child classifiers
    # 'reddit' replaces '_' special value in child
    # 'chrome' is a static tag from the parent ProcessClassifier
    equal(result.tags, ['reddit', 'chrome'])

    ###

    result = classifiers['chrome'].get(chrome_iplayer)
    equal(result.project, 'Casual')

    # Description parsed using regex pattern
    equal(result.description, 'Requiem - Series 1: Episode 1')
    equal(result.tags, ['chrome'])

    ###

    result = classifiers['chrome'].get(chrome_netflix)
    equal(result.project, 'Casual')

    # 'netflix' replaces '_' special value
    equal(result.description, 'netflix')
    equal(result.tags, ['chrome'])


def test_config():
    config = test_common.get_test_config()
    equal(midnight(config.date), midnight(datetime.datetime.today()))

    file_config = config.as_json()

    config2 = Config(clargs={}, json_data=file_config)
    equal(
        config.as_json(), config2.as_json(),
        comment='Building from dumped json should yield equal object')

    file_config.update(default_day='yesterday')
    config = Config(clargs={}, json_data=file_config)
    equal(config.date,
          midnight(datetime.datetime.today() - timedelta(days=1)))

    # Test integer workspace ID is read as an integer
    file_config.update(default_workspace='20')
    config = Config(clargs={}, json_data=file_config)
    equal(config.default_workspace, 20)

    clargs = {
        'key': TEST_API_KEY,
        'default_workspace': TEST_WORKSPACE,
        'minimum_event_seconds': 60,
        'day_ends_at': 3,
        'day': 'yesterday',
        'date': '15-10-02',
        'local': False,
        'render': False,
        'reset': False,
        'showall': False,
    }
    # Test parsing of date with partial year
    config = Config(json_data=file_config, clargs=Bunch(clargs))
    equal(config.date, datetime.datetime(2015, 10, 2))

    # Test parsing of date with full year
    clargs.update(date='2015-10-03')
    config = Config(json_data=file_config, clargs=Bunch(clargs))
    equal(config.date, datetime.datetime(2015, 10, 3))

    return config


def test_db_consume():
    start = datetime.datetime(2015, 6, 12, 9, 0, 0)
    data = [
        (
            'chrome',
            'beatonma.org',
            int((start + timedelta(hours=x)).timestamp()),
            False
        ) for x in range(1, 7)
    ]

    with autotoggl.DatabaseManager(filename=autotoggl.DB_PATH) as db:
        sql = '''INSERT INTO toggl VALUES (?, ?, ?, ?)'''
        for x in data:
            db.exec(sql, x)

    # Consume events
    events = [
        autotoggl.Event(
            id=n+1,
            process=x[0],
            title=x[1],
            start=x[2],
            consumed=x[3])
        for n, x in enumerate(data)
    ]
    for e in events[:-1]:
        e.consumed = True

    # Add final event to merged id list of the previous event
    events[-2].merged.append(events[-1].id)

    with autotoggl.DatabaseManager(filename=autotoggl.DB_PATH) as db:
        db.consume(events)

        # Test DatabaseManager.consume()
        sql = '''SELECT consumed FROM toggl WHERE rowid=?'''
        for e in events:
            equal(
                db.exec(sql, (e.id,)).fetchone()[0],
                1)

        # test DatabaseManager.reset()
        db.reset(start, start + timedelta(days=1))
        for e in events:
            equal(
                db.exec(sql, (e.id,)).fetchone()[0],
                0)

    os.remove(autotoggl.DB_PATH)
