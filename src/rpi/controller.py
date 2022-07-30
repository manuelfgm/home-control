from datetime import time
from datetime import datetime
import enum

class ControlResult(enum.IntEnum):
    NO_ACTION = 0
    TURN_ON = 1
    TURN_OFF = 2
    ERROR = 3

class Controller:
    def __init__(self,
                start = time(hour = 18, minute = 0, second = 0, microsecond = 0),
                stop = time(hour = 22, minute = 0, second = 0, microsecond = 0),
                usert = 20.0,
                backt = 18.0):
        self.__time_start = start
        self.__time_stop = stop
        self.__user_temp = usert
        self.__back_temp = backt
        self.__target_temp = self.__back_temp

    @classmethod
    def fromdict(cls, datadic):
        time_start = datetime.strptime(datadic["time_start"], "%H:%M").time()
        time_stop = datetime.strptime(datadic["time_stop"], "%H:%M").time()
        user_temp = datadic["user_temp"]
        back_temp = datadic["back_temp"]
        return cls(
            start = time_start,
            stop = time_stop,
            usert = user_temp,
            backt = back_temp,
        )

    def get_time_start(self):
        return self.__time_start


    def set_time_start(self, value):
        self.__time_start = value


    def get_time_stop(self):
        return self.__time_stop


    def set_time_stop(self, value):
        self.__time_stop = value


    def get_user_temp(self):
        return self.__user_temp


    def set_user_temp(self, value):
        self.__user_temp = round(value, 1)


    def get_back_temp(self):
        return self.__back_temp


    def set_back_temp(self, value):
        self.__back_temp = round(value, 1)


    def get_back_temp(self):
        return self.__back_temp

    def get_target_temp(self):
        return self.__target_temp


    def control(self, temp, time):
        if time >= self.__time_start and time <= self.__time_stop:
            self.__target_temp = self.__user_temp
        else:
            self.__target_temp = self.__back_temp

        if round(temp, 1) < self.__target_temp:
            return ControlResult.TURN_ON
        elif round(temp, 1) > self.__target_temp:
            return ControlResult.TURN_OFF
        else:
            return ControlResult.NO_ACTION

