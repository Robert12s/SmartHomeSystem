from database import Database
from models import Task


class Scheduler:
    def __init__(self, db: Database):
        self.db = db

    def addTask(self, task: Task) -> bool:
        query = '''
            INSERT INTO tasks (name, location, time, repeat, deviceId)
            VALUES (?, ?, ?, ?, ?)
        '''
        params = (
            task.name,
            task.location,
            task.time,
            task.repeat,
            task.device.id
        )
        cursor = self.db.executeQuery(query, params)
        return cursor is not None

    def getTasks(self) -> list:
        query = "SELECT * FROM tasks"
        cursor = self.db.executeQuery(query)
        return cursor.fetchall() if cursor else []

    def runTasks(self):
        # Implementation would go here
        pass