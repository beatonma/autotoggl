import datetime
import json

from datetime import timedelta
from random import choice, random

from autotoggl import (
    categorise_events,
    compress_events,
    calculate_event_durations,
)

EVENTS_DAY_ONE = [
    {'process': 'studio64', 'title': 'Commons - [/path/to/project] - FileName.java - Android Studio 3.0.1', 'timestamp': datetime.datetime(2018, 1, 30, 9, 20, 45).timestamp()},
    {'process': 'sublime_text', 'title': '/gdbackup/gdbackup.py (gdbackup) - Sublime Text', 'timestamp': datetime.datetime(2018, 1, 30, 9, 22, 45).timestamp()},
    {'process': 'chrome', 'title': 'reddit: the front page of the internet', 'timestamp': datetime.datetime(2018, 1, 30, 9, 23, 30).timestamp()},
    {'process': 'chrome', 'title': 'reddit: the front page of the internet', 'timestamp': datetime.datetime(2018, 1, 30, 9, 24, 15).timestamp()},
    {'process': 'studio64', 'title': 'Commons - [/path/to/project] - FileName.java - Android Studio 3.0.1', 'timestamp': datetime.datetime(2018, 1, 30, 9, 26, 15).timestamp()},
    {'process': 'studio64', 'title': 'Commons - [/path/to/project] - FileName.java - Android Studio 3.0.1', 'timestamp': datetime.datetime(2018, 1, 30, 9, 28, 15).timestamp()},
    {'process': 'chrome', 'title': 'reddit: the front page of the internet', 'timestamp': datetime.datetime(2018, 1, 30, 9, 30, 15).timestamp()},
    {'process': 'chrome', 'title': 'StarCraft on Reddit', 'timestamp': datetime.datetime(2018, 1, 30, 9, 32, 15).timestamp()},
    {'process': 'sublime_text', 'title': '/auto-toggl/main.py (auto-toggl) - Sublime Text', 'timestamp': datetime.datetime(2018, 1, 30, 11, 2, 15).timestamp()},
    {'process': 'chrome', 'title': 'reddit: the front page of the internet', 'timestamp': datetime.datetime(2018, 1, 30, 11, 3).timestamp()},
    {'process': 'studio64', 'title': 'Commons - [/path/to/project] - FileName.java - Android Studio 3.0.1', 'timestamp': datetime.datetime(2018, 1, 30, 11, 33).timestamp()},
    {'process': 'studio64', 'title': 'Commons - [/path/to/project] - FileName.java - Android Studio 3.0.1', 'timestamp': datetime.datetime(2018, 1, 30, 13, 3).timestamp()},
    {'process': 'studio64', 'title': 'Commons - [/path/to/project] - FileName.java - Android Studio 3.0.1', 'timestamp': datetime.datetime(2018, 1, 30, 13, 5).timestamp()},
    {'process': 'chrome', 'title': 'Politics', 'timestamp': datetime.datetime(2018, 1, 30, 14, 35).timestamp()},
    {'process': 'studio64', 'title': 'CommonsManager - [/path/to/project] - FileName.java - Android Studio 3.0.1', 'timestamp': datetime.datetime(2018, 1, 30, 16, 5).timestamp()},
]
EVENTS_DAY_TWO = [
    {'timestamp': datetime.datetime(2018, 1, 30, 9, 51).timestamp(), 'process': 'studio64', 'title': 'CommonsManager - [/path/to/project] - FileName.java - Android Studio 3.0.1'},
    {'timestamp': datetime.datetime(2018, 1, 30, 9, 53).timestamp(), 'process': 'chrome', 'title': 'StarCraft on Reddit'},
    {'timestamp': datetime.datetime(2018, 1, 30, 9, 54, 30).timestamp(), 'process': 'studio64', 'title': 'LEDControl - [/path/to/project] - FileName.java - Android Studio 3.0.1'},
    {'timestamp': datetime.datetime(2018, 1, 30, 10, 24, 30).timestamp(), 'process': 'chrome', 'title': 'Politics'},
    {'timestamp': datetime.datetime(2018, 1, 30, 10, 26).timestamp(), 'process': 'chrome', 'title': 'StarCraft on Reddit'},
    {'timestamp': datetime.datetime(2018, 1, 30, 10, 27, 30).timestamp(), 'process': 'studio64', 'title': 'CommonsManager - [/path/to/project] - FileName.java - Android Studio 3.0.1'},
    {'timestamp': datetime.datetime(2018, 1, 30, 10, 29).timestamp(), 'process': 'studio64', 'title': 'CommonsManager - [/path/to/project] - FileName.java - Android Studio 3.0.1'},
    {'timestamp': datetime.datetime(2018, 1, 30, 10, 30, 30).timestamp(), 'process': 'studio64', 'title': 'LEDControl - [/path/to/project] - FileName.java - Android Studio 3.0.1'},
    {'timestamp': datetime.datetime(2018, 1, 30, 10, 31, 15).timestamp(), 'process': 'studio64', 'title': 'Commons - [/path/to/project] - FileName.java - Android Studio 3.0.1'},
    {'timestamp': datetime.datetime(2018, 1, 30, 10, 32).timestamp(), 'process': 'chrome', 'title': 'reddit: the front page of the internet'},
    {'timestamp': datetime.datetime(2018, 1, 30, 10, 32, 45).timestamp(), 'process': 'studio64', 'title': 'LEDControl - [/path/to/project] - FileName.java - Android Studio 3.0.1'},
    {'timestamp': datetime.datetime(2018, 1, 30, 10, 34, 15).timestamp(), 'process': 'chrome', 'title': 'reddit: the front page of the internet'},
    {'timestamp': datetime.datetime(2018, 1, 30, 10, 35).timestamp(), 'process': 'chrome', 'title': 'Politics'},
    {'timestamp': datetime.datetime(2018, 1, 30, 10, 37).timestamp(), 'process': 'studio64', 'title': 'CommonsManager - [/path/to/project] - FileName.java - Android Studio 3.0.1'},
    {'timestamp': datetime.datetime(2018, 1, 30, 10, 37, 45).timestamp(), 'process': 'chrome', 'title': 'Politics'},
]
EVENTS_DAY_THREE = [
    {'duration': 0, 'title': 'StarCraft on Reddit', 'process': 'chrome', 'timestamp': datetime.datetime(2018, 1, 30, 10, 22).timestamp()},
    {'duration': 0, 'title': 'Commons - [/path/to/project] - FileName.java - Android Studio 3.0.1', 'process': 'studio64', 'timestamp': datetime.datetime(2018, 1, 30, 10, 23, 30).timestamp()},
    {'duration': 0, 'title': '/gdbackup/gdbackup.py (gdbackup) - Sublime Text', 'process': 'sublime_text', 'timestamp': datetime.datetime(2018, 1, 30, 10, 23, 50).timestamp()},
    {'duration': 0, 'title': '__SYS__', 'process': 'System.Idle', 'timestamp': datetime.datetime(2018, 1, 30, 10, 24, 35).timestamp()},
    {'duration': 0, 'title': 'LEDControl - [/path/to/project] - FileName.java - Android Studio 3.0.1', 'process': 'studio64', 'timestamp': datetime.datetime(2018, 1, 30, 10, 25, 5).timestamp()},
    {'duration': 0, 'title': 'StarCraft on Reddit', 'process': 'chrome', 'timestamp': datetime.datetime(2018, 1, 30, 11, 55, 5).timestamp()},
    {'duration': 0, 'title': 'CommonsManager - [/path/to/project] - FileName.java - Android Studio 3.0.1', 'process': 'studio64', 'timestamp': datetime.datetime(2018, 1, 30, 11, 55, 25).timestamp()},
    {'duration': 0, 'title': 'StarCraft on Reddit', 'process': 'chrome', 'timestamp': datetime.datetime(2018, 1, 30, 11, 56, 10).timestamp()},
    {'duration': 0, 'title': '/gdbackup/gdbackup.py (gdbackup) - Sublime Text', 'process': 'sublime_text', 'timestamp': datetime.datetime(2018, 1, 30, 11, 56, 55).timestamp()},
    {'duration': 0, 'title': '/gdbackup/gdbackup.py (gdbackup) - Sublime Text', 'process': 'sublime_text', 'timestamp': datetime.datetime(2018, 1, 30, 11, 58, 25).timestamp()},
    {'duration': 0, 'title': '__SYS__', 'process': 'System.SessionLock', 'timestamp': datetime.datetime(2018, 1, 30, 12, 28, 25).timestamp()},
    {'duration': 0, 'title': '__SYS__', 'process': 'System.SessionUnlock', 'timestamp': datetime.datetime(2018, 1, 30, 12, 28, 55).timestamp()},
    {'duration': 0, 'title': 'Commons - [/path/to/project] - FileName.java - Android Studio 3.0.1', 'process': 'studio64', 'timestamp': datetime.datetime(2018, 1, 30, 12, 30, 55).timestamp()},
    {'duration': 0, 'title': 'Commons - [/path/to/project] - FileName.java - Android Studio 3.0.1', 'process': 'studio64', 'timestamp': datetime.datetime(2018, 1, 30, 14, 0, 55).timestamp()},
    {'duration': 0, 'title': 'LEDControl - [/path/to/project] - FileName.java - Android Studio 3.0.1', 'process': 'studio64', 'timestamp': datetime.datetime(2018, 1, 30, 14, 1).timestamp()},
    {'duration': 0, 'title': 'LEDControl - [/path/to/project] - FileName.java - Android Studio 3.0.1', 'process': 'studio64', 'timestamp': datetime.datetime(2018, 1, 30, 14, 1, 5).timestamp()},
    {'duration': 0, 'title': '/gdbackup/gdbackup.py (gdbackup) - Sublime Text', 'process': 'sublime_text', 'timestamp': datetime.datetime(2018, 1, 30, 14, 3, 5).timestamp()},
    {'duration': 0, 'title': '__SYS__', 'process': 'System.UnIdle', 'timestamp': datetime.datetime(2018, 1, 30, 14, 3, 10).timestamp()},
    {'duration': 0, 'title': 'CommonsManager - [/path/to/project] - FileName.java - Android Studio 3.0.1', 'process': 'studio64', 'timestamp': datetime.datetime(2018, 1, 30, 14, 3, 15).timestamp()},
    {'duration': 0, 'title': '/auto-toggl/main.py (auto-toggl) - Sublime Text', 'process': 'sublime_text', 'timestamp': datetime.datetime(2018, 1, 30, 14, 3, 45).timestamp()},
    {'duration': 0, 'title': '/gdbackup/gdbackup.py (gdbackup) - Sublime Text', 'process': 'sublime_text', 'timestamp': datetime.datetime(2018, 1, 30, 14, 4, 30).timestamp()},
    {'duration': 0, 'title': 'LEDControl - [/path/to/project] - FileName.java - Android Studio 3.0.1', 'process': 'studio64', 'timestamp': datetime.datetime(2018, 1, 30, 14, 6).timestamp()},
    {'duration': 0, 'title': '__SYS__', 'process': 'System.UnIdle', 'timestamp': datetime.datetime(2018, 1, 30, 14, 6, 5).timestamp()},
    {'duration': 0, 'title': 'Politics', 'process': 'chrome', 'timestamp': datetime.datetime(2018, 1, 30, 15, 36, 5).timestamp()},
    {'duration': 0, 'title': 'LEDControl - [/path/to/project] - FileName.java - Android Studio 3.0.1', 'process': 'studio64', 'timestamp': datetime.datetime(2018, 1, 30, 15, 38, 5).timestamp()},
]


def generate_events(howmany=15):
    MAX_EVENT_DURATION = 60 * 60  # 1hr
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
                'timestamp': time,
                'duration': 0,
            }
        )

    for x in events:
        print('{},'.format(x))
    return events


# generate_events(25)
# raise(SystemExit())

events = EVENTS_DAY_THREE

calculate_event_durations(events)
events = list(filter(lambda x: x['duration'], events))
events.sort(key=lambda x: x['timestamp'])
assert(len(events) == 10)
print(json.dumps(events, indent=2))

EXPECTED_VALUES = [
    {
        'duration': 185,
        'title': 'StarCraft on Reddit',
        'process': 'chrome',
        'timestamp': '10:22:00'
    },
    {
        'duration': 5510,
        'title': 'LEDControl - [/path/to/project] - FileName.java - Android Studio 3.0.1',
        'process': 'studio64',
        'timestamp': '10:25:05'
    },
    {
        'duration': 90,
        'title': '/gdbackup/gdbackup.py (gdbackup) - Sublime Text',
        'process': 'sublime_text',
        'timestamp': '11:56:55'
    },
    {
        'duration': 1830,
        'title': '/gdbackup/gdbackup.py (gdbackup) - Sublime Text',
        'process': 'sublime_text',
        'timestamp': '11:58:25'
    },
    {
        'duration': 120,
        'title': '__SYS__',
        'process': 'System.SessionUnlock',
        'timestamp': '12:28:55'
    },
    {
        'duration': 5410,
        'title': 'Commons - [/path/to/project] - FileName.java - Android Studio 3.0.1',
        'process': 'studio64',
        'timestamp': '12:30:55'
    },
    {
        'duration': 205,
        'title': 'LEDControl - [/path/to/project] - FileName.java - Android Studio 3.0.1',
        'process': 'studio64',
        'timestamp': '14:01:05'
    },
    {
        'duration': 95,
        'title': '/gdbackup/gdbackup.py (gdbackup) - Sublime Text',
        'process': 'sublime_text',
        'timestamp': '14:04:30'
    },
    {
        'duration': 5400,
        'title': '__SYS__',
        'process': 'System.UnIdle',
        'timestamp': '14:06:05'
    },
    {
        'duration': 120,
        'title': 'Politics',
        'process': 'chrome',
        'timestamp': '15:36:05'
    },
]

for x, y in zip(events, EXPECTED_VALUES):
    print(
        '  ACTUAL: {} {} {}\n'
        'EXPECTED: {} {} {}'
        .format(
            int(x['duration']),
            x['process'],
            datetime.datetime.fromtimestamp(x['timestamp']),
            int(y['duration']),
            y['process'],
            y['timestamp'],
        ))
    print('difference={}s'.format(int(y['duration'] - x['duration'])))

    assert(int(x['duration']) == int(y['duration']))
    assert(x['process'] == y['process'])
    assert(x['title'] == y['title'])
