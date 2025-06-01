from datetime import datetime, time
import time as tm


class Scheduler:
    def __init__(self, db):
        self.db = db

    def addTask(self, deviceId, action, scheduledTime, repeat=False):
        query = """INSERT INTO tasks (deviceId, action, time, repeat) 
                   VALUES (?,?,?,?)"""
        return self.db.execute(query, (deviceId, action, scheduledTime, repeat))

    def getTasks(self):
        c = self.db.execute("SELECT * FROM tasks")
        return c.fetchall() if c else []

    def runPendingTasks(self, deviceManager):
        tasks = self.getTasks()
        currentTime = datetime.now().strftime("%H:%M")

        for task in tasks:
            _, deviceId, action, taskTime, repeat = task

            if taskTime == currentTime:
                device = deviceManager.getDeviceById(deviceId)
                if device:
                    if "on" in action.lower():
                        device.turnOn()
                    elif "off" in action.lower():
                        device.turnOff()
                    elif "brightness" in action.lower():
                        value = int(action.split()[-1])
                        if isinstance(device, Light):
                            device.setBrightness(value)
                    elif "temperature" in action.lower():
                        value = float(action.split()[-1])
                        if isinstance(device, Thermostat):
                            device.setTemperature(value)
                    elif "arm" in action.lower():
                        if isinstance(device, Alarm):
                            device.arm()
                    elif "disarm" in action.lower():
                        if isinstance(device, Alarm):
                            device.disarm()

                    deviceManager.updateDevice(device)

                    if not repeat:
                        self.db.execute("DELETE FROM tasks WHERE id=?", (task[0],))