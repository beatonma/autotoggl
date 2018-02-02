'''
This script is run by python2 in EventGhost
'''

import eg
import os
import sqlite3
import time

from win32gui import GetForegroundWindow, GetWindowText

DB_PATH = os.path.expanduser('~/autotoggl/toggl.db')

SYSTEM_EVENTS = [
    'System.SessionLock',
    'System.SessionUnlock',
    'System.Idle',
    'System.UnIdle',
]
IGNORE_PROCESSES = [
    'explorer',
    'powershell',
    'ShellExperienceHost',
    'SearchUI',
    'OpenWith',
    'LockApp',
    'Desktop',
    'ApplicationFrameHost'
]


def _init_db():
    exists = False
    if os.path.exists(DB_PATH):
        exists = True
    else:
        try:
            os.makedirs(os.path.dirname(DB_PATH))
            print('Created autotoggl directory: {}'.format(DB_PATH))
        except:
            print('Unable to make directory {}'.format(DB_PATH))
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if exists:
        return conn, cursor

    sql = '''CREATE TABLE toggl
             (process_name TEXT NOT NULL,
              window_title TEXT NOT NULL,
              start INTEGER NOT NULL)'''
    cursor.execute(sql)
    return conn, cursor


def _add(cursor, process_name, window_title):
    print(process_name, window_title)
    sql = '''INSERT INTO toggl VALUES (?, ?, ?, ?)'''
    cursor.execute(
        sql,
        (
            process_name,
            window_title,
            int(time.time()),
            False
        )
    )


# Main
event_name = eg.event.string

if event_name in SYSTEM_EVENTS:
    title = '__SYS__'
    process_name = event_name
else:
    title = unicode(GetWindowText(GetForegroundWindow()).decode(
        'windows-1250', 'ignore'))
    process_name = unicode(event_name.split('.')[-1].decode(
        'windows-1250', 'ignore'))

if not title:
    # Ignore windows with empty titles
    raise SystemExit()

if process_name in IGNORE_PROCESSES:
    # Ignore unwanted processes
    raise SystemExit()
    
conn, cursor = _init_db()
try:
    _add(cursor, process_name, title)
    conn.commit()
except Exception as e:
    print(e)
cursor.close()
conn.close()