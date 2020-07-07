import sqlite3


def db_connect(location):
    try:
        conn = sqlite3.connect(location)
        return conn
    except sqlite3.Error as e:
        print(e)
        return None
