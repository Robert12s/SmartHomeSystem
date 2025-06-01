import tkinter as tk
from tkinter import ttk, messagebox
from models import Light, Thermostat, Alarm
from database import Database
from scheduler import Scheduler


class SmartHomeSystem:
    def __init__(self, db: Database):
        self.db = db
        self.scheduler = Scheduler(db)

    def addDevice(self, name: str, location: str, device_type: str, **kwargs):
        query = '''
            INSERT INTO devices 
            (name, location, status, voltage, brightness, temperature, armed)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        '''

        if device_type == "Light":
            brightness = kwargs.get('brightness', 50)
            params = (name, location, False, 0.0, brightness, None, None)
            device = Light(0, name, location, False, 0.0, brightness)
        elif device_type == "Thermostat":
            temperature = kwargs.get('temperature', 22.0)
            params = (name, location, False, 0.0, None, temperature, None)
            device = Thermostat(0, name, location, False, 0.0, temperature)
        elif device_type == "Alarm":
            armed = kwargs.get('armed', False)
            params = (name, location, False, 0.0, None, None, armed)
            device = Alarm(0, name, location, False, 0.0, armed)

        if device:
            cursor = self.db.executeQuery(query, params)
            if cursor:
                device.id = cursor.lastrowid
                return device
        return None

    def getDeviceById(self, id: int):
        query = "SELECT * FROM devices WHERE id = ?"
        cursor = self.db.executeQuery(query, (id,))
        if cursor:
            row = cursor.fetchone()
            if row:
                return self._createDeviceFromRow(row)
        return None

    def getAllDevices(self):
        query = "SELECT * FROM devices"
        cursor = self.db.executeQuery(query)
        devices = []
        if cursor:
            for row in cursor.fetchall():
                device = self._createDeviceFromRow(row)
                if device:
                    devices.append(device)
        return devices

    def _createDeviceFromRow(self, row: tuple):
        (id, name, location, status, voltage,
         brightness, temperature, armed) = row

        if brightness is not None:
            return Light(id, name, location, status, voltage, brightness)
        elif temperature is not None:
            return Thermostat(id, name, location, status, voltage, temperature)
        elif armed is not None:
            return Alarm(id, name, location, status, voltage, armed)
        return None


class SmartHomeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Home System")

        # Initialize database and system
        self.db = Database()
        self.system = SmartHomeSystem(self.db)

        # Create GUI elements
        self.createWidgets()
        self.refreshDeviceList()

    def createWidgets(self):
        # [Same GUI implementation as before]
        # ...
        pass

    def add_device(self):
        device_type = self.device_type_var.get()
        name = self.device_name_var.get()
        location = self.device_location_var.get()

        if not name or not location:
            messagebox.showerror("Error", "Please enter both name and location")
            return

        device = self.system.addDevice(name, location, device_type)
        if device:
            messagebox.showinfo("Success", f"{device_type} added successfully")
            self.refreshDeviceList()
        else:
            messagebox.showerror("Error", "Failed to add device")

    def refreshDeviceList(self):
        # [Same device list refresh as before]
        pass

    def toggle_device(self, turn_on: bool):
        # [Same device toggle as before]
        pass


if __name__ == "__main__":
    root = tk.Tk()
    app = SmartHomeGUI(root)
    root.mainloop()