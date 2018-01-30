'''
This script is run by python2 in EventGhost
'''

import eg
import os
import sqlite3
import time

from win32gui import GetForegroundWindow, GetWindowText

DB_PATH = os.path.expanduser('~/toggl.db')


def _init_db():
    exists = False
    if os.path.exists(DB_PATH):
        exists = True
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if exists:
        return conn, cursor

    sql = '''CREATE TABLE toggl (
             process_name TEXT NOT NULL,
             window_title TEXT NOT NULL,
             timestamp INTEGER NOT NULL
             )'''
    cursor.execute(sql)
    return conn, cursor


def _add(cursor, process_name, window_title):
    print(process_name, window_title)
    sql = '''INSERT INTO toggl VALUES (?, ?, ?)'''
    cursor.execute(
        sql,
        (
            process_name,
            window_title,
            int(time.time())
        )
    )


event_name = eg.event.string
system_events = [
    'System.SessionLock',
    'System.SessionUnlock',
    'System.Idle',
    'System.UnIdle',
]

if event_name in system_events:
    title = '__SYS__'
    process_name = event_name
else:
    title = unicode(GetWindowText(GetForegroundWindow())
                    .decode('windows-1250', 'ignore'))
    process_name = unicode(event_name.split('.')[-1]
                           .decode('windows-1250', 'ignore'))

if not title:
    # Ignore windows with empty titles
    raise(SystemExit())

conn, cursor = _init_db()
try:
    _add(cursor, process_name, title)
    conn.commit()
except Exception as e:
    print(e)
cursor.close()
conn.close()
