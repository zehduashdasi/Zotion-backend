import sqlite3 as sq

def setup():
    try:
        conn = sq.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS users")
        cursor.execute("DROP TABLE IF EXISTS todo")
        cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, password TEXT NOT NULL)")
        cursor.execute("CREATE TABLE todo (id INTEGER PRIMARY KEY AUTOINCREMENT, user INTEGER NOT NULL, title TEXT NOT NULL, content TEXT)")
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(e)
    finally:
        conn.close()

def setup_post():
    try:
        conn = sq.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM todo")
        cursor.execute("INSERT INTO todo (user,title, content) VALUES (?,?,?)",(1,"first todo list","go to *horizons* **equinox** [ ]"))

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(e)
    finally:
        conn.close()

setup()