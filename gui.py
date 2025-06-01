import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from models import Light, Thermostat, Alarm
from scheduler import Scheduler


class SmartHomeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Home System")

        self.db = Database()
        self.scheduler = Scheduler(self.db)
        self.setupUI()
        self.loadDevices()

    def setupUI(self):
        mainFrame = ttk.Frame(self.root, padding="10")
        mainFrame.pack(fill=tk.BOTH, expand=True)

        # Device List
        self.tree = ttk.Treeview(mainFrame, columns=('type', 'location', 'status'))
        self.tree.heading('#0', text='Name')
        self.tree.heading('type', text='Type')
        self.tree.heading('location', text='Location')
        self.tree.heading('status', text='Status')
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Control Buttons
        btnFrame = ttk.Frame(mainFrame)
        btnFrame.pack(fill=tk.X, pady=5)

        ttk.Button(btnFrame, text="Turn On", command=lambda: self.setDeviceStatus(True)).pack(side=tk.LEFT)
        ttk.Button(btnFrame, text="Turn Off", command=lambda: self.setDeviceStatus(False)).pack(side=tk.LEFT)

        # Task Scheduling
        taskFrame = ttk.LabelFrame(mainFrame, text="Schedule Task")
        taskFrame.pack(fill=tk.X, pady=5)

        ttk.Button(taskFrame, text="Check Tasks", command=self.scheduler.runPendingTasks).pack()

    def loadDevices(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        c = self.db.execute("SELECT * FROM devices")
        for device in c.fetchall():
            status = "On" if device[4] else "Off"
            self.tree.insert('', 'end', text=device[1],
                             values=(device[2], device[3], status))

    def setDeviceStatus(self, status):
        selected = self.tree.focus()
        if selected:
            device_name = self.tree.item(selected)['text']
            query = "UPDATE devices SET status=? WHERE name=?"
            if self.db.execute(query, (status, device_name)):
                self.loadDevices()


if __name__ == "__main__":
    root = tk.Tk()
    app = SmartHomeGUI(root)
    root.mainloop()