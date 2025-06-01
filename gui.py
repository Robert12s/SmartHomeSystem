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
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Device list
        self.device_list = ttk.Treeview(self.main_frame, columns=('name', 'location', 'status'), show='headings')
        self.device_list.heading('name', text='Name')
        self.device_list.heading('location', text='Location')
        self.device_list.heading('status', text='Status')
        self.device_list.grid(row=0, column=0, columnspan=3, pady=10)

        # Add device controls
        ttk.Label(self.main_frame, text="Add New Device:").grid(row=1, column=0, sticky=tk.W)

        self.device_type_var = tk.StringVar()
        self.device_type_combo = ttk.Combobox(self.main_frame, textvariable=self.device_type_var,
                                              values=["Light", "Thermostat", "Alarm"])
        self.device_type_combo.grid(row=2, column=0, padx=5, pady=5)

        ttk.Label(self.main_frame, text="Name:").grid(row=2, column=1, sticky=tk.E)
        self.device_name_var = tk.StringVar()
        ttk.Entry(self.main_frame, textvariable=self.device_name_var).grid(row=2, column=2, padx=5, pady=5)

        ttk.Label(self.main_frame, text="Location:").grid(row=3, column=1, sticky=tk.E)
        self.device_location_var = tk.StringVar()
        ttk.Entry(self.main_frame, textvariable=self.device_location_var).grid(row=3, column=2, padx=5, pady=5)

        ttk.Button(self.main_frame, text="Add Device", command=self.add_device).grid(row=4, column=2, pady=10)

        # Control buttons
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.grid(row=5, column=0, columnspan=3)

        ttk.Button(self.control_frame, text="Turn On", command=lambda: self.toggle_device(True)).grid(row=0, column=0,
                                                                                                      padx=5)
        ttk.Button(self.control_frame, text="Turn Off", command=lambda: self.toggle_device(False)).grid(row=0, column=1,
                                                                                                        padx=5)
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
        # Clear existing items
        for item in self.device_tree.get_children():
            self.device_tree.delete(item)

        # Add devices from database
        devices = self.device_service.getAllDevices()
        for device in devices:
            self.device_tree.insert("", "end", values=(
                device.getName(),
                device.getLocation(),
                "On" if device.getStatus() else "Off"
            ))

    pass

    def toggle_device(self, turn_on: bool):
        selected_item = self.device_tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "No device selected")
            return

        device_name = self.device_tree.item(selected_item)['values'][0]
        devices = self.device_service.getAllDevices()

        for device in devices:
            if device.getName() == device_name:
                if turn_on:
                    device.turnOn()
                else:
                    device.turnOff()
                break

        self.refresh_device_list()
        pass


if __name__ == "__main__":
    root = tk.Tk()
    app = SmartHomeGUI(root)
    root.mainloop()