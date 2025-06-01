class Scheduler:
    def __init__(self, db):
        self.db = db

    def addTask(self, deviceId, action, time, repeat=False):
        query = "INSERT INTO tasks (deviceId, action, time, repeat) VALUES (?,?,?,?)"
        return self.db.execute(query, (deviceId, action, time, repeat))

    def getTasks(self):
        tasks = []
        c = self.db.execute("SELECT * FROM tasks")
        if c:
            for task in c.fetchall():
                tasks.append(task)
        return tasks