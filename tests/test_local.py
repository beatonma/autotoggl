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


class Bunch:
    '''Dictionary wrapper'''
    def __init__(self, adict):
        self.__dict__.update(adict)


def generate_events():
    EVENT_LIST = [
        ('chrome', 'reddit: the front page of the internet'),
        ('sublime_text', '/auto-toggl/autotoggl.py (auto-toggl) - Sublime Text'),
        ('powershell', 'Windows Powershell'),
        ('chrome', 'Google'),
        ('System.Idle', '__SYS__'),
        ('System.UnIdle', '__SYS__'),
        ('sublime_text', '/auto-toggl/autotoggl.py (auto-toggl) - Sublime Text'),
        ('explorer', 'C:\\some\\path'),
        ('sublime_text', '/auto-toggl/autotoggl.py (auto-toggl) - Sublime Text'),
        ('explorer', 'C:\\some\\path'),
        ('powershell', 'Windows Powershell'),
        ('chrome', 'Politics'),
        ('chrome', 'StarCraft on Reddit'),
        ('System.SessionLock', '__SYS__'),
        ('System.SessionUnlock', '__SYS__'),
        ('chrome', 'beatonma (Michael Beaton) - GitHub'),
        ('studio64', 'Commons - [/path/to/project] - File.java - Android Studio'),
        ('explorer', 'C:\\some\\path'),
        ('explorer', 'C:\\some\\other\\path'),
        ('chrome', 'Google'),
        ('System.Idle', '__SYS__'),
        ('System.UnIdle', '__SYS__'),
        ('sublime_text', '/gdbackup/gdbackup.py (gdbackup) - Sublime Text'),
        ('System.SessionLogoff', '__SYS__'),
    ]
    EVENT_LENGTHS = [
        45,
        90,
        120,
        900,   # 15 mins
        1800,  # 30 mins
        3600,  # 60 mins
        5400,  # 90 mins
    ]

    time = datetime.datetime(2018, 6, 12, 9)
    events = []
    for e in EVENT_LIST:
        process = e[0]
        title = e[1]
        if title == '__SYS__':
            delta = random.choice(EVENT_LENGTHS[:3])
        else:
            delta = random.choice(EVENT_LENGTHS)
        time = time + timedelta(seconds=delta)
        ev = {
            'process': process,
            'title': title,
            'start': time,
        }
        print('{},'.format(ev))
        events.append(ev)

    return events


def test_compress_events():
    test_events = [
        {'process': 'chrome', 'title': 'reddit: the front page of the internet', 'start': int(datetime.datetime(2018, 6, 12, 10, 30).timestamp())},
        {'process': 'sublime_text', 'title': '/auto-toggl/autotoggl.py (auto-toggl) - Sublime Text', 'start': int(datetime.datetime(2018, 6, 12, 11, 30).timestamp())},
        {'process': 'powershell', 'title': 'Windows Powershell', 'start': int(datetime.datetime(2018, 6, 12, 13, 0).timestamp())},
        {'process': 'chrome', 'title': 'Google', 'start': int(datetime.datetime(2018, 6, 12, 14, 0).timestamp())},
        {'process': 'System.Idle', 'title': '__SYS__', 'start': int(datetime.datetime(2018, 6, 12, 14, 1, 30).timestamp())},
        {'process': 'System.UnIdle', 'title': '__SYS__', 'start': int(datetime.datetime(2018, 6, 12, 14, 3, 30).timestamp())},
        {'process': 'sublime_text', 'title': '/auto-toggl/autotoggl.py (auto-toggl) - Sublime Text', 'start': int(datetime.datetime(2018, 6, 12, 14, 5).timestamp())},
        {'process': 'explorer', 'title': 'C:\\some\\path', 'start': int(datetime.datetime(2018, 6, 12, 14, 7).timestamp())},
        {'process': 'sublime_text', 'title': '/auto-toggl/autotoggl.py (auto-toggl) - Sublime Text', 'start': int(datetime.datetime(2018, 6, 12, 14, 22).timestamp())},
        {'process': 'explorer', 'title': 'C:\\some\\path', 'start': int(datetime.datetime(2018, 6, 12, 14, 24).timestamp())},
        {'process': 'powershell', 'title': 'Windows Powershell', 'start': int(datetime.datetime(2018, 6, 12, 15, 54).timestamp())},
        {'process': 'chrome', 'title': 'Politics', 'start': int(datetime.datetime(2018, 6, 12, 15, 54, 45).timestamp())},
        {'process': 'chrome', 'title': 'StarCraft on Reddit', 'start': int(datetime.datetime(2018, 6, 12, 16, 54, 45).timestamp())},
        {'process': 'System.SessionLock', 'title': '__SYS__', 'start': int(datetime.datetime(2018, 6, 12, 16, 55, 30).timestamp())},
        {'process': 'System.SessionUnlock', 'title': '__SYS__', 'start': int(datetime.datetime(2018, 6, 12, 16, 56, 15).timestamp())},
        {'process': 'chrome', 'title': 'beatonma (Michael Beaton) - GitHub', 'start': int(datetime.datetime(2018, 6, 12, 18, 26, 15).timestamp())},
        {'process': 'studio64', 'title': 'Commons - [/path/to/project] - File.java - Android Studio', 'start': int(datetime.datetime(2018, 6, 12, 18, 27, 45).timestamp())},
        {'process': 'explorer', 'title': 'C:\\some\\path', 'start': int(datetime.datetime(2018, 6, 12, 18, 57, 45).timestamp())},
        {'process': 'explorer', 'title': 'C:\\some\\other\\path', 'start': int(datetime.datetime(2018, 6, 12, 19, 27, 45).timestamp())},
        {'process': 'chrome', 'title': 'Google', 'start': int(datetime.datetime(2018, 6, 12, 19, 28, 30).timestamp())},
        {'process': 'System.Idle', 'title': '__SYS__', 'start': int(datetime.datetime(2018, 6, 12, 19, 30).timestamp())},
        {'process': 'System.UnIdle', 'title': '__SYS__', 'start': int(datetime.datetime(2018, 6, 12, 19, 31, 30).timestamp())},
        {'process': 'sublime_text', 'title': '/gdbackup/gdbackup.py (gdbackup) - Sublime Text', 'start': int(datetime.datetime(2018, 6, 12, 19, 32, 15).timestamp())},
        {'process': 'System.SessionLogoff', 'title': '__SYS__', 'start': int(datetime.datetime(2018, 6, 12, 19, 34, 15).timestamp())},
    ]

    expected_values = [
        {
            'process': 'chrome',
            'title': 'reddit: the front page of the internet',
            'start': int(datetime.datetime(2018, 6, 12, 10, 30).timestamp()),
            'duration': 3600
        },
        {
            'process': 'sublime_text',
            'title': '/auto-toggl/autotoggl.py (auto-toggl) - Sublime Text',
            'start': int(datetime.datetime(2018, 6, 12, 11, 30).timestamp()),
            'duration': 9090
        },
        {
            'process': 'sublime_text',
            'title': '/auto-toggl/autotoggl.py (auto-toggl) - Sublime Text',
            'start': int(datetime.datetime(2018, 6, 12, 14, 5).timestamp()),
            'duration': 6585
        },
        {
            'process': 'chrome',
            'title': 'Politics',
            'start': int(datetime.datetime(2018, 6, 12, 15, 54, 45).timestamp()),
            'duration': 3645
        },
        {
            'process': 'studio64',
            'title': 'Commons - [/path/to/project] - File.java - Android Studio',
            'start': int(datetime.datetime(2018, 6, 12, 18, 27, 45).timestamp()),
            'duration': 3735
        },
        {
            'process': 'sublime_text',
            'title': '/gdbackup/gdbackup.py (gdbackup) - Sublime Text',
            'start': int(datetime.datetime(2018, 6, 12, 19, 32, 15).timestamp()),
            'duration': 120
        }
    ]

    config = test_common.get_test_config()

    events = [autotoggl.Event(**x) for x in test_events]
    autotoggl.categorise_events(events, config.defs())
    events = autotoggl.compress_events(events, config)

    equal(len(events), len(expected_values), data=events)

    for x, y in zip(events, expected_values):
        equal(x.start, y['start'], data=[x, y])
        equal(x.process, y['process'], data=[x, y])
        equal(x.title, y['title'], data=[x, y])
        equal(int(x.duration), int(y['duration']), data=[x, y])

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
    equal(result.tags, ['py'])

    # As above, but replace project name with an alias
    result = classifiers['sublime_text'].get(sublimetext_with_alias)
    equal(result.project, 'Home Assistant')  # 'gassistant' -> 'Home Assistant'
    equal(result.description, 'settings.py')
    equal(result.tags, ['py'])

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
        'clean': None,
        'ns': None,
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


def test_get_total_duration():
    events = [
        autotoggl.Event(duration=20),
        autotoggl.Event(duration=123),
        autotoggl.Event(duration=456),
    ]
    equal(
        autotoggl.get_total_duration(events),
        599)
