import enum

class ControlResult(enum.IntEnum):
    NO_ACTION = 0
    TURN_ON = 1
    TURN_OFF = 2
    ERROR = 3

class AirCond:
    def __init__(self,
                name = "unkonw",
                mac = "",
                on_temp = 35.0,
                off_temp = 30.0,
                manual_mode = False):
        self.name = name
        self.mac = mac
        self.on_temp = round(on_temp, 1)
        self.off_temp = round(off_temp, 1)
        self.manual = manual_mode

    @classmethod
    def fromdict(cls, datadic):
        dev_name = datadic["name"]
        dev_mac = datadic["mac"]
        ont = datadic["on_temp"]
        offt = datadic["off_temp"]
        offforce = datadic["manual_mode"]
        return cls(name = dev_name,
                   mac = dev_mac,
                   on_temp = ont,
                   off_temp = offt,
                   off_force = offforce)
    
    def set_name(self, value):
        self.name = value

    def set_mac(self, value):
        self.mac = value

    def set_on_temp(self, value):
        self.on_temp = value

    def set_off_temp(self, value):
        self.off_temp = value

    def set_off_force(self, value):
        self.off_force = value

    def control(self, temp):
        if self.off_force == True:
            return ControlResult.NO_ACTION
            
        if(round(temp, 1) < self.off_temp) or \
            (self.off_force == True):
            return ControlResult.TURN_OFF
        elif(round(temp, 1) > self.on_temp):
            return ControlResult.TURN_ON
        else:
            return ControlResult.NO_ACTION


