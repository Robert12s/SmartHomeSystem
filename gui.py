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
        query = "INSERT INTO devices (name, type, location) VALUES (?, ?, ?)"
        cursor = self.db.execute(query, (name, deviceType, location))
        return cursor.lastrowid if cursor else None

    def getDeviceById(self, deviceId):
        cursor = self.db.execute("SELECT * FROM devices WHERE id=?", (deviceId,))
        row = cursor.fetchone() if cursor else None
        if not row:
            return None

        id, name, type, loc, status, brightness, temp, armed, voltage = row
        if type == "Light":
            return Light(id, name, loc, status, brightness or 50)
        elif type == "Thermostat":
            return Thermostat(id, name, loc, status, temp or 22.0)
        elif type == "Alarm":
            return Alarm(id, name, loc, status, armed or False)
        return None

    def getAllDevices(self):
        devices = []
        cursor = self.db.execute("SELECT * FROM devices")
        for row in cursor.fetchall():
            device = self.getDeviceById(row[0])
            if device:
                devices.append(device)
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
        self.root.geometry("1000x700")

        self.db = Database()
        self.deviceManager = DeviceManager(self.db)
        self.scheduler = Scheduler(self.db)

        self.setupUI()
        self.loadDevices()
        self.checkScheduledTasks()

    def setupUI(self):
        mainFrame = ttk.Frame(self.root, padding=10)
        mainFrame.pack(fill=tk.BOTH, expand=True)

        # Left Panel - Devices
        leftPanel = ttk.Frame(mainFrame)
        leftPanel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Energy Monitoring (at the top)
        energyFrame = ttk.LabelFrame(leftPanel, text="Energy Monitoring", padding=10)
        energyFrame.pack(fill=tk.X, pady=5)

        self.energyLabel = ttk.Label(energyFrame, text="Total Energy Usage: 0.00 kWh")
        self.energyLabel.pack()

        # Scrollable Device Tree
        treeFrame = ttk.Frame(leftPanel)
        treeFrame.pack(fill=tk.BOTH, expand=True)

        treeScroll = ttk.Scrollbar(treeFrame)
        treeScroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(treeFrame, columns=('type', 'location', 'status', 'value', 'energy'),
                                 yscrollcommand=treeScroll.set, height=12)
        treeScroll.config(command=self.tree.yview)

        self.tree.heading('#0', text='Name')
        self.tree.heading('type', text='Type')
        self.tree.heading('location', text='Location')
        self.tree.heading('status', text='Status')
        self.tree.heading('value', text='Value')
        self.tree.heading('energy', text='Energy (kWh)')

        self.tree.column('#0', width=120)
        self.tree.column('type', width=80)
        self.tree.column('location', width=100)
        self.tree.column('status', width=60)
        self.tree.column('value', width=80)
        self.tree.column('energy', width=80)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Device Controls
        controlFrame = ttk.Frame(leftPanel)
        controlFrame.pack(fill=tk.X, pady=5)

        ttk.Button(controlFrame, text="Turn On", command=lambda: self.setDeviceStatus(True)).pack(side=tk.LEFT)
        ttk.Button(controlFrame, text="Turn Off", command=lambda: self.setDeviceStatus(False)).pack(side=tk.LEFT)

        # Add Device Panel
        addFrame = ttk.LabelFrame(leftPanel, text="Add New Device", padding=10)
        addFrame.pack(fill=tk.X, pady=5)

        ttk.Label(addFrame, text="Type:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.deviceType = ttk.Combobox(addFrame, values=['Light', 'Thermostat', 'Alarm'])
        self.deviceType.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)

        ttk.Label(addFrame, text="Name:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.deviceName = ttk.Entry(addFrame)
        self.deviceName.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)

        ttk.Label(addFrame, text="Location:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.deviceLocation = ttk.Entry(addFrame)
        self.deviceLocation.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)

        ttk.Button(addFrame, text="Add Device", command=self.addDevice).grid(row=3, column=1, pady=5, sticky=tk.E)

        # Right Panel - Scheduling
        rightPanel = ttk.Frame(mainFrame)
        rightPanel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, expand=True)

        # Schedule New Task
        taskFrame = ttk.LabelFrame(rightPanel, text="Schedule Task", padding=10)
        taskFrame.pack(fill=tk.X, pady=5)

        ttk.Label(taskFrame, text="Device:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.taskDevice = ttk.Combobox(taskFrame)
        self.taskDevice.grid(row=0, column=1, pady=2, sticky=tk.EW)

        ttk.Label(taskFrame, text="Action:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.taskAction = ttk.Combobox(taskFrame, values=[
            "Turn On", "Turn Off",
            "Set Brightness 50", "Set Brightness 100",
            "Set Temperature 20", "Set Temperature 25",
            "Arm", "Disarm"
        ])
        self.taskAction.grid(row=1, column=1, pady=2, sticky=tk.EW)

        ttk.Label(taskFrame, text="Time (HH:MM):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.taskTime = ttk.Entry(taskFrame)
        self.taskTime.grid(row=2, column=1, pady=2, sticky=tk.EW)

        self.taskRepeat = tk.BooleanVar()
        ttk.Checkbutton(taskFrame, text="Repeat Daily", variable=self.taskRepeat).grid(row=3, column=1, sticky=tk.W,
                                                                                       pady=2)

        ttk.Button(taskFrame, text="Schedule Task", command=self.scheduleTask).grid(row=4, column=1, pady=5,
                                                                                    sticky=tk.E)

        # Scheduled Tasks List
        taskListFrame = ttk.LabelFrame(rightPanel, text="Scheduled Tasks", padding=10)
        taskListFrame.pack(fill=tk.BOTH, expand=True)

        self.taskTree = ttk.Treeview(taskListFrame, columns=('action', 'time', 'repeat'))
        self.taskTree.heading('#0', text='Device')
        self.taskTree.heading('action', text='Action')
        self.taskTree.heading('time', text='Time')
        self.taskTree.heading('repeat', text='Repeats')

        self.taskTree.column('#0', width=120)
        self.taskTree.column('action', width=100)
        self.taskTree.column('time', width=80)
        self.taskTree.column('repeat', width=60)
        self.taskTree.pack(fill=tk.BOTH, expand=True)

    def loadDevices(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for item in self.taskTree.get_children():
            self.taskTree.delete(item)

        devices = self.deviceManager.getAllDevices()
        deviceNames = []
        totalEnergy = 0.0

        for device in devices:
            if device:
                status = "On" if device.status else "Off"
                energy = device.getEnergyUsage()
                totalEnergy += energy

                # Set value based on device type
                value = "-"
                if isinstance(device, Light):
                    value = f"{device.brightness}%"
                elif isinstance(device, Thermostat):
                    value = f"{device.temperature}°C"
                elif isinstance(device, Alarm):
                    value = "Armed" if device.armed else "Disarmed"

                self.tree.insert('', 'end', text=device.name,
                                 values=(device.type, device.location,
                                         status, value, f"{energy:.2f}"))
                deviceNames.append(device.name)

        # Update energy monitoring
        self.energyLabel.config(text=f"Total Energy Usage: {totalEnergy:.2f} kWh")
        self.taskDevice['values'] = deviceNames

        # Load scheduled tasks
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
            self.taskTime.delete(0, tk.END)
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