import sqlite3 as sq

def setup():
    try:
        conn = sq.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS users")
        cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, password TEXT NOT NULL)")
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(e)
    finally:
        conn.close()

setup()