class Device:
    def __init__(self, id, name, location, status=False):
        self.id = id
        self.name = name
        self.location = location
        self.status = status

    def turnOn(self): self.status = True

    def turnOff(self): self.status = False


class Light(Device):
    def __init__(self, id, name, location, status=False, brightness=50):
        super().__init__(id, name, location, status)
        self.brightness = brightness


class Thermostat(Device):
    def __init__(self, id, name, location, status=False, temperature=22.0):
        super().__init__(id, name, location, status)
        self.temperature = temperature


class Alarm(Device):
    def __init__(self, id, name, location, status=False, armed=False):
        super().__init__(id, name, location, status)
        self.armed = armed

    def arm(self): self.armed = True

    def disarm(self): self.armed = False


class Task:
    def __init__(self, id, device, action, time, repeat=False):
        self.id = id
        self.device = device
        self.action = action
        self.time = time
        self.repeat = repeat