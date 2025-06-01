from datetime import datetime


class Scheduler:
    def __init__(self, db):
        self.db = db

    def addTask(self, deviceId, action, time, repeat=False):
        query = "INSERT INTO tasks (deviceId, action, time, repeat) VALUES (?,?,?,?)"
        return self.db.execute(query, (deviceId, action, time, repeat))

    def getTasks(self):
        c = self.db.execute("SELECT * FROM tasks")
        return c.fetchall() if c else []

    def runPendingTasks(self):
        tasks = self.getTasks()
        current_time = datetime.now().strftime("%H:%M")
        for task in tasks:
            if task[3] == current_time:  # task[3] is time
                print(f"Executing task: {task}")  # Replace with actual device control