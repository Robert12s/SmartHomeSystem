import sqlite3


class Database:
    def __init__(self):
        self.conn = sqlite3.connect('smart_home.db')
        self.createTables()

    def createTables(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS devices
                    (id INTEGER PRIMARY KEY, 
                     name TEXT, 
                     type TEXT,
                     location TEXT,
                     status BOOLEAN DEFAULT 0,
                     brightness INTEGER DEFAULT 50,
                     temperature REAL DEFAULT 22.0,
                     armed BOOLEAN DEFAULT 0,
                     voltage REAL DEFAULT 0)''')

        c.execute('''CREATE TABLE IF NOT EXISTS tasks
                    (id INTEGER PRIMARY KEY,
                     deviceId INTEGER,
                     action TEXT,
                     time TEXT,
                     repeat BOOLEAN DEFAULT 0)''')
        self.conn.commit()

    def execute(self, query, params=()):
        try:
            c = self.conn.cursor()
            c.execute(query, params)
            self.conn.commit()
            return c
        except Exception as e:
            print(f"Database error: {e}")
            return None