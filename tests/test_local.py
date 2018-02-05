import datetime
import json
import os

from datetime import timedelta
from random import choice

import autotoggl.autotoggl
from autotoggl.autotoggl import (
    Event,
    categorise_event,
    categorise_events,
    compress_events,
    load_config,
    submit,
)
from autotoggl.config import Config
from autotoggl.util import midnight

from autotoggl.render import render_events

from tests import test_common
from tests.test_credentials import (
    TEST_WORKSPACE,
    TEST_WORKSPACE_ID,
    TEST_API_KEY,
)


logger = test_common.get_logger(__file__)
autotoggl.logger = logger
autotoggl.BASE_DIR = os.path.expanduser('~/autotoggl/test/')


def _equal(actual, expected, data=None):
    try:
        assert(expected == actual)
    except AssertionError as e:
        logger.warn('ASSERTION ERROR (NOT EQUAL):')
        logger.warn('  Expected: {}'.format(expected))
        logger.warn('    Actual: {}'.format(actual))
        if data:
            try:
                logger.warn('  Data: {}'.format(json.dumps(data, indent=2)))
            except:
                logger.warn('  Data: {}'.format(data))
        raise SystemExit()


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
        time = time + timedelta(seconds=choice(EVENT_LENGTHS))
        e = choice(EVENT_TYPES)
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
        events = [Event(**x) for x in EVENTS]

    events = compress_events(events, config)
    for e in events:
        categorise_event(e, config.defs())

    EXPECTED_VALUES = [
        {'duration': 155, 'title': 'StarCraft on Reddit', 'process': 'chrome', 'start': '10:22:00'},
        {'duration': 5510, 'title': 'LEDControl - [/path/to/project] - FileName.java - Android Studio 3.0.1', 'process': 'studio64', 'start': '10:25:05'},
        {'duration': 1890, 'title': '/gdbackup/gdbackup.py (gdbackup) - Sublime Text', 'process': 'sublime_text', 'start': '11:56:55'},
        {'duration': 5410, 'title': 'Commons - [/path/to/project] - FileName.java - Android Studio 3.0.1', 'process': 'studio64', 'start': '12:30:55'},
        {'duration': 125, 'title': 'LEDControl - [/path/to/project] - FileName.java - Android Studio 3.0.1', 'process': 'studio64', 'start': '14:01:05'},
        {'duration': 95, 'title': '/gdbackup/gdbackup.py (gdbackup) - Sublime Text', 'process': 'sublime_text', 'start': '14:04:30'},
        {'duration': 120, 'title': 'Politics', 'process': 'chrome', 'start': '15:36:05'},
    ]

    _equal(len(events), len(EXPECTED_VALUES), data=events)

    for x, y in zip(events, EXPECTED_VALUES):
        _equal(int(x.duration), int(y['duration']), data=[x, y])
        _equal(x.process, y['process'], data=[x, y])
        _equal(x.title, y['title'], data=[x, y])

    render_events(events)


def test_project_definitions(config=None):
    config = test_common.get_test_config()
    _equal(categorise_event(Event(**{
            'title': 'Duolingo',
            'process': 'chrome'
        }), config.defs()), 'Duolingo')

    _equal(categorise_event(Event(**{
            'title': '/auto-toggl/main.py (auto-toggl) - Sublime Text',
            'process': 'sublime_text'
        }), config.defs()), 'auto-toggl')

    _equal(categorise_event(Event(**{
            'title': 'LEDControl - [/path/to/proj] - File.java - Android Studio 3.0',
            'process': 'studio64'
        }), config.defs()), 'LEDControl')

    # Confirm that categorise_event correctly parses project and description
    # and adds those data to the original event object
    event = Event(**{
        'title': 'LEDControl - [/path/to/proj] - File.java - Android Studio 3.0',
        'process': 'studio64'
    })
    categorise_event(event, config.defs())
    _equal(event.project, 'LEDControl')
    _equal(event.description, 'File.java')


# def test_api_interface(config=None):
#     config = test_common.get_test_config()
#     interface = TogglApiInterface(config)
    # j = interface.get_workspaces()
    # logger.info(json.dumps(j, indent=2))
    # test_api_get_projects(interface)
    # pid = test_api_create_project(interface)
    # test_api_create_time_entry(interface, pid)
    # test_api_delete_project(interface, pid)
    # logger.info(interface)


# def test_api_get_projects(interface):
#     j = interface.get_all_projects()


# def test_api_create_project(interface):
#     j = interface.create_project('API_TEST_PROJECT', TEST_WORKSPACE_ID)
#     _equal(j['data']['wid'], TEST_WORKSPACE_ID)

#     pid = j['data']['id']
#     return pid


# def test_api_create_time_entry(interface, pid):
#     j = interface.create_time_entry(
#         pid,
#         (datetime.datetime.now(timezone.utc).astimezone() - timedelta(hours=1))
#         .replace(microsecond=0).isoformat(),
#         120
#     )
#     logger.debug('Time entry response: {}'.format(j))


# def test_api_delete_project(interface, pid):
#     sleep(10)
#     deleted = interface.delete_project(pid)
#     _equal(deleted, True)


def test_config():
    config = test_common.get_test_config()
    _equal(midnight(config.date), midnight(datetime.datetime.today()))

    file_config = config.as_json()

    file_config.update(default_day='yesterday')
    config = Config(json_data=file_config)
    _equal(config.date,
           midnight(datetime.datetime.today() - timedelta(days=1)))

    # Test integer workspace ID is read as an integer
    file_config.update(default_workspace='20')
    config = Config(json_data=file_config)
    _equal(config.default_workspace, 20)

    clargs = {
        'key': TEST_API_KEY,
        'default_workspace': TEST_WORKSPACE,
        'minimum_event_seconds': 60,
        'day_ends_at': 3,
        'day': 'yesterday',
        'date': '15-10-02',
        'local': False
    }
    # Test parsing of date with partial year
    config = Config(json_data=file_config, clargs=Bunch(clargs))
    _equal(config.date, datetime.datetime(2015, 10, 2))

    # Test parsing of date with full year
    clargs.update(date='2015-10-03')
    config = Config(json_data=file_config, clargs=Bunch(clargs))
    _equal(config.date, datetime.datetime(2015, 10, 3))

    return config


if __name__ == '__main__':
    logger.info('test_config...')
    config = test_config()
    logger.info('test_project_definitions...')
    test_project_definitions(config)
    logger.info('test_calculate_event_durations...')
    test_calculate_event_durations([Event(**x) for x in EVENTS], config)

    # logger.info('test_api_interface...')
    # test_api_interface(config)

    logger.info('')
    logger.info('Tests complete!')
