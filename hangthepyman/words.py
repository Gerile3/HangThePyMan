import sqlite3


def random_word(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM wlist ORDER BY RANDOM() LIMIT 1;")
    try:
        word = cur.fetchone()
        return word
    except (sqlite3.Error, sqlite3.OperationalError):
        print("Error: Could not open database.")
