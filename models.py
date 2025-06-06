class Device:
    def __init__(self, id, name, type, location, status=False, voltage=0):
        self.id = id
        self.name = name
        self.type = type
        self.location = location
        self.status = status
        self.voltage = voltage

    def turnOn(self):
        self.status = True
        self.voltage = 10

    def turnOff(self):
        self.status = False
        self.voltage = 0

    def getEnergyUsage(self):
        return self.voltage * 0.1


class Light(Device):
    def __init__(self, id, name, location, status=False, brightness=50):
        super().__init__(id, name, "Light", location, status)
        self.brightness = brightness
        self.voltage = 5 + (brightness * 0.1)

    def setBrightness(self, value):
        self.brightness = max(0, min(100, value))
        self.voltage = 5 + (self.brightness * 0.1)
        print(f"Brightness set to {self.brightness}")

class Thermostat(Device):
    def __init__(self, id, name, location, status=False, temperature=22.0):
        super().__init__(id, name, "Thermostat", location, status)
        self.temperature = temperature
        self.voltage = 15 + abs(22 - temperature)

    def setTemperature(self, value):
        self.temperature = max(10.0, min(30.0, value))
        self.voltage = 15 + abs(22 - self.temperature)  # More energy when heating/cooling
        print(f"Temperature set to {self.temperature}")

class Alarm(Device):
    def __init__(self, id, name, location, status=False, armed=False):
        super().__init__(id, name, "Alarm", location, status)
        self.armed = armed
        self.voltage = 2 if armed else 0

    def arm(self):
        self.armed = True
        self.voltage = 2
        print("Alarm armed")

    def disarm(self):
        self.armed = False
        self.voltage = 0
        print("Alarm disarmed")

class Task:
    def __init__(self, id, deviceId, action, time, repeat=False):
        self.id = id
        self.deviceId = deviceId
        self.action = action
        self.time = time
        self.repeat = repeat