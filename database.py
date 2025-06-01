import sqlite3
from typing import Optional, List, Dict, Any


class Database:
    def __init__(self, dbName: str = "smart_home.db"):
        self.connection = sqlite3.connect(dbName)
        self.createTables()

    def createTables(self):
        cursor = self.connection.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                location TEXT NOT NULL,
                status BOOLEAN DEFAULT 0,
                voltage REAL DEFAULT 0,
                brightness INTEGER,
                temperature REAL,
                armed BOOLEAN
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                location TEXT NOT NULL,
                time TEXT NOT NULL,
                repeat BOOLEAN DEFAULT 0,
                deviceId INTEGER,
                FOREIGN KEY (deviceId) REFERENCES devices(id)
            )
        ''')

        self.connection.commit()

    def executeQuery(self, query: str, params: tuple = ()) -> Optional[sqlite3.Cursor]:
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            return cursor
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None

    def close(self):
        self.connection.close()