import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import Database
from models import Light, Thermostat, Alarm
from scheduler import Scheduler


class DeviceManager:
    def __init__(self, db):
        self.db = db

    def addDevice(self, name, deviceType, location):
        query = "INSERT INTO devices (name, type, location) VALUES (?,?,?)"
        c = self.db.execute(query, (name, deviceType, location))
        return c.lastrowid if c else None

    def getDeviceById(self, deviceId):
        c = self.db.execute("SELECT * FROM devices WHERE id=?", (deviceId,))
        row = c.fetchone() if c else None
        if not row:
            return None

        # Ensure we have all 9 columns, filling missing ones with defaults
        row = list(row)
        while len(row) < 9:  # Add missing columns with default values
            row.append(None)

        id, name, type, loc, status, bright, temp, armed, voltage = row

        # Provide defaults for None values
        bright = 50 if bright is None else bright
        temp = 22.0 if temp is None else temp
        armed = False if armed is None else armed
        voltage = 0 if voltage is None else voltage

        if type == "Light":
            return Light(id, name, loc, status, bright)
        elif type == "Thermostat":
            return Thermostat(id, name, loc, status, temp)
        elif type == "Alarm":
            return Alarm(id, name, loc, status, armed)
        return None

    def getAllDevices(self):
        devices = []
        c = self.db.execute("SELECT * FROM devices")
        for row in c.fetchall():
            id = row[0]
            devices.append(self.getDeviceById(id))
        return devices

    def updateDevice(self, device):
        query = """UPDATE devices SET 
                   status=?, brightness=?, temperature=?, 
                   armed=?, voltage=? WHERE id=?"""
        params = (
            device.status,
            getattr(device, 'brightness', None),
            getattr(device, 'temperature', None),
            getattr(device, 'armed', None),
            device.voltage,
            device.id
        )
        return self.db.execute(query, params)


class SmartHomeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Home System")
        self.root.geometry("900x700")

        self.db = Database()
        self.deviceManager = DeviceManager(self.db)
        self.scheduler = Scheduler(self.db)

        self.setupUI()
        self.loadDevices()
        self.checkScheduledTasks()

    def setupUI(self):
        mainFrame = ttk.Frame(self.root, padding=10)
        mainFrame.pack(fill=tk.BOTH, expand=True)

        # Device List (Left Panel)
        leftPanel = ttk.Frame(mainFrame)
        leftPanel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(leftPanel, columns=('type', 'location', 'status', 'energy'))
        self.tree.heading('#0', text='Name')
        self.tree.heading('type', text='Type')
        self.tree.heading('location', text='Location')
        self.tree.heading('status', text='Status')
        self.tree.heading('energy', text='Energy Usage')
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Device Controls
        controlFrame = ttk.Frame(leftPanel)
        controlFrame.pack(fill=tk.X, pady=5)

        ttk.Button(controlFrame, text="Turn On", command=lambda: self.setDeviceStatus(True)).pack(side=tk.LEFT)
        ttk.Button(controlFrame, text="Turn Off", command=lambda: self.setDeviceStatus(False)).pack(side=tk.LEFT)

        # Add Device Panel
        addFrame = ttk.LabelFrame(leftPanel, text="Add New Device")
        addFrame.pack(fill=tk.X, pady=5)

        ttk.Label(addFrame, text="Type:").grid(row=0, column=0, padx=5, pady=5)
        self.deviceType = ttk.Combobox(addFrame, values=['Light', 'Thermostat', 'Alarm'])
        self.deviceType.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(addFrame, text="Name:").grid(row=1, column=0, padx=5, pady=5)
        self.deviceName = ttk.Entry(addFrame)
        self.deviceName.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(addFrame, text="Location:").grid(row=2, column=0, padx=5, pady=5)
        self.deviceLocation = ttk.Entry(addFrame)
        self.deviceLocation.grid(row=2, column=1, padx=5, pady=5)

        ttk.Button(addFrame, text="Add Device", command=self.addDevice).grid(row=3, column=1, pady=5)

        # Task Scheduling (Right Panel)
        rightPanel = ttk.Frame(mainFrame)
        rightPanel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10)

        taskFrame = ttk.LabelFrame(rightPanel, text="Schedule Task", padding=10)
        taskFrame.pack(fill=tk.BOTH, pady=5)

        ttk.Label(taskFrame, text="Device:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.taskDevice = ttk.Combobox(taskFrame)
        self.taskDevice.grid(row=0, column=1, pady=2)

        ttk.Label(taskFrame, text="Action:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.taskAction = ttk.Combobox(taskFrame, values=[
            "Turn On", "Turn Off",
            "Set Brightness 50", "Set Brightness 100",
            "Set Temperature 20", "Set Temperature 25",
            "Arm", "Disarm"
        ])
        self.taskAction.grid(row=1, column=1, pady=2)

        ttk.Label(taskFrame, text="Time (HH:MM):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.taskTime = ttk.Entry(taskFrame)
        self.taskTime.grid(row=2, column=1, pady=2)

        self.taskRepeat = tk.BooleanVar()
        ttk.Checkbutton(taskFrame, text="Repeat Daily", variable=self.taskRepeat).grid(row=3, column=1, sticky=tk.W,
                                                                                       pady=2)

        ttk.Button(taskFrame, text="Schedule Task", command=self.scheduleTask).grid(row=4, column=1, pady=5)

        # Task List
        taskListFrame = ttk.LabelFrame(rightPanel, text="Scheduled Tasks", padding=10)
        taskListFrame.pack(fill=tk.BOTH, expand=True)

        self.taskTree = ttk.Treeview(taskListFrame, columns=('action', 'time', 'repeat'))
        self.taskTree.heading('#0', text='Device')
        self.taskTree.heading('action', text='Action')
        self.taskTree.heading('time', text='Time')
        self.taskTree.heading('repeat', text='Repeats')
        self.taskTree.pack(fill=tk.BOTH, expand=True)

        # Energy Monitoring
        energyFrame = ttk.LabelFrame(leftPanel, text="Energy Monitoring", padding=10)
        energyFrame.pack(fill=tk.X, pady=5)

        self.energyLabel = ttk.Label(energyFrame, text="Total Energy Usage: 0 kWh")
        self.energyLabel.pack()

    def loadDevices(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for item in self.taskTree.get_children():
            self.taskTree.delete(item)

        devices = self.deviceManager.getAllDevices()
        deviceNames = []

        totalEnergy = 0
        for device in devices:
            if device:
                status = "On" if device.status else "Off"
                energy = device.getEnergyUsage()
                totalEnergy += energy

                self.tree.insert('', 'end', text=device.name,
                                 values=(device.type, device.location,
                                         status, f"{energy:.2f} kWh"))
                deviceNames.append(device.name)

        self.taskDevice['values'] = deviceNames
        self.energyLabel.config(text=f"Total Energy Usage: {totalEnergy:.2f} kWh")

        # Load tasks
        tasks = self.scheduler.getTasks()
        for task in tasks:
            device = self.deviceManager.getDeviceById(task[1])
            if device:
                self.taskTree.insert('', 'end', text=device.name,
                                     values=(task[2], task[3],
                                             "Yes" if task[4] else "No"))

    def addDevice(self):
        name = self.deviceName.get()
        deviceType = self.deviceType.get()
        location = self.deviceLocation.get()

        if not all([name, deviceType, location]):
            messagebox.showerror("Error", "Please fill all fields")
            return

        if self.deviceManager.addDevice(name, deviceType, location):
            self.loadDevices()
            self.deviceName.delete(0, tk.END)
            self.deviceLocation.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Failed to add device")

    def setDeviceStatus(self, status):
        selected = self.tree.focus()
        if not selected:
            return

        deviceName = self.tree.item(selected)['text']
        devices = self.deviceManager.getAllDevices()
        device = next((d for d in devices if d and d.name == deviceName), None)

        if device:
            if status:
                device.turnOn()
            else:
                device.turnOff()

            if self.deviceManager.updateDevice(device):
                self.loadDevices()

    def scheduleTask(self):
        deviceName = self.taskDevice.get()
        action = self.taskAction.get()
        taskTime = self.taskTime.get()
        repeat = self.taskRepeat.get()

        if not all([deviceName, action, taskTime]):
            messagebox.showerror("Error", "Please fill all fields")
            return

        try:
            datetime.strptime(taskTime, "%H:%M")
        except ValueError:
            messagebox.showerror("Error", "Please enter time in HH:MM format")
            return

        devices = self.deviceManager.getAllDevices()
        device = next((d for d in devices if d and d.name == deviceName), None)

        if device and self.scheduler.addTask(device.id, action, taskTime, repeat):
            self.loadDevices()
            messagebox.showinfo("Success", "Task scheduled successfully")
        else:
            messagebox.showerror("Error", "Failed to schedule task")

    def checkScheduledTasks(self):
        self.scheduler.runPendingTasks(self.deviceManager)
        self.loadDevices()
        self.root.after(60000, self.checkScheduledTasks)  # Check every minute


if __name__ == "__main__":
    root = tk.Tk()
    app = SmartHomeGUI(root)
    root.mainloop()