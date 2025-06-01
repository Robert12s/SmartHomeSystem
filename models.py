from abc import ABC, abstractmethod

class Device(ABC):
    def __init__(self, id: int, name: str, location: str, status: bool = False, voltage: float = 0.0):
        self.id = id
        self.name = name
        self.location = location
        self.status = status
        self.voltage = voltage

    def turnOn(self):
        self.status = True

    def turnOff(self):
        self.status = False

    def getStatus(self) -> bool:
        return self.status

    def setStatus(self, status: bool):
        self.status = status

    def getVoltage(self) -> float:
        return self.voltage

    def setVoltage(self, voltage: float):
        self.voltage = voltage

    def getName(self) -> str:
        return self.name

    def getLocation(self) -> str:
        return self.location

    @abstractmethod
    def configure(self):
        pass


class Light(Device):
    def __init__(self, id: int, name: str, location: str, status: bool = False, voltage: float = 0.0,
                 brightness: int = 50):
        super().__init__(id, name, location, status, voltage)
        self.brightness = brightness

    def configure(self):
        return {
            "brightness": self.brightness
        }

    def setBrightness(self, brightness: int):
        if 0 <= brightness <= 100:
            self.brightness = brightness

    def getBrightness(self) -> int:
        return self.brightness


class Thermostat(Device):
    def __init__(self, id: int, name: str, location: str, status: bool = False, voltage: float = 0.0,
                 temperature: float = 22.0):
        super().__init__(id, name, location, status, voltage)
        self.temperature = temperature

    def configure(self):
        return {
            "temperature": self.temperature
        }

    def setTemperature(self, temperature: float):
        self.temperature = temperature

    def getTemperature(self) -> float:
        return self.temperature


class Alarm(Device):
    def __init__(self, id: int, name: str, location: str, status: bool = False, voltage: float = 0.0,
                 armed: bool = False):
        super().__init__(id, name, location, status, voltage)
        self.armed = armed

    def configure(self):
        return {
            "armed": self.armed
        }

    def arm(self):
        self.armed = True

    def disarm(self):
        self.armed = False

    def isArmed(self) -> bool:
        return self.armed


class Task:
    def __init__(self, id: int, name: str, location: str, time: str, repeat: bool, device: Device):
        self.id = id
        self.name = name
        self.location = location
        self.time = time
        self.repeat = repeat
        self.device = device