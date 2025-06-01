import tkinter as tk
from tkinter import ttk, messagebox


class SmartHomeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Home System")

        # Setup database and services
        self.db = Database()
        self.scheduler = Scheduler(self.db)

        # Create UI
        self.setupUI()
        self.loadDevices()

    def setupUI(self):
        # Device List
        self.deviceTree = ttk.Treeview(self.root, columns=('name', 'location', 'status'))
        self.deviceTree.heading('#0', text='ID')
        self.deviceTree.heading('name', text='Name')
        self.deviceTree.heading('location', text='Location')
        self.deviceTree.heading('status', text='Status')
        self.deviceTree.pack(fill=tk.BOTH, expand=True)

        # Control Buttons
        btnFrame = ttk.Frame(self.root)
        btnFrame.pack(fill=tk.X)

        ttk.Button(btnFrame, text="Turn On", command=lambda: self.setDeviceStatus(True)).pack(side=tk.LEFT)
        ttk.Button(btnFrame, text="Turn Off", command=lambda: self.setDeviceStatus(False)).pack(side=tk.LEFT)

        # Add Device
        addFrame = ttk.Frame(self.root)
        addFrame.pack(fill=tk.X)

        self.deviceType = ttk.Combobox(addFrame, values=['Light', 'Thermostat', 'Alarm'])
        self.deviceType.pack(side=tk.LEFT)
        ttk.Button(addFrame, text="Add Device", command=self.addDevice).pack(side=tk.LEFT)

    def loadDevices(self):
        for item in self.deviceTree.get_children():
            self.deviceTree.delete(item)

        c = self.db.execute("SELECT * FROM devices")
        if c:
            for device in c.fetchall():
                self.deviceTree.insert('', 'end', text=device[0], values=device[1:4])

    def addDevice(self):
        deviceType = self.deviceType.get()
        if not deviceType:
            return

        query = "INSERT INTO devices (name, location, type) VALUES (?,?,?)"
        if self.db.execute(query, (f"New {deviceType}", "Room", deviceType)):
            self.loadDevices()

    def setDeviceStatus(self, status):
        selected = self.deviceTree.focus()
        if selected:
            deviceId = self.deviceTree.item(selected)['text']
            query = "UPDATE devices SET status=? WHERE id=?"
            if self.db.execute(query, (status, deviceId)):
                self.loadDevices()


if __name__ == "__main__":
    root = tk.Tk()
    app = SmartHomeGUI(root)
    root.mainloop()