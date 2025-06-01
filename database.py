import sqlite3


class Database:
    def __init__(self):
        self.conn = sqlite3.connect('smart_home.db')
        self.createTables()

    def createTables(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS devices
                     (id INTEGER PRIMARY KEY, name TEXT, location TEXT, 
                      type TEXT, status BOOLEAN, brightness INTEGER, 
                      temperature REAL, armed BOOLEAN)''')
        c.execute('''CREATE TABLE IF NOT EXISTS tasks
                     (id INTEGER PRIMARY KEY, deviceId INTEGER, action TEXT, 
                      time TEXT, repeat BOOLEAN)''')
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