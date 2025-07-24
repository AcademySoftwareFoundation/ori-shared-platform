from enum import Enum

def FormatNumber(v):
    num_digits = 5
    try:
        if v != 0 and abs(v) < .1**num_digits:
            return '%.2e' % v
        elif (v % 1) < .1**num_digits:
            return str(int(v))
        else:
            return str(round(v, num_digits))
    except:
        return '0'

class Slider(Enum):
    GAMMA = "gamma"
    WHITEPOINT = "whitepoint"
    BLACKPOINT = "blackpoint"
    FSTOP = "gain"
    FALLOFF = "falloff"
    LIFT = "lift"
    POWER = "power"
    OFFSET = "offset"
    SLOPE = "slope"
    SAT = "saturation"

class SliderAttrs:
    def __init__(self):
        self.__data = {}

    def set_value(self, index:Slider, value:dict):
        self.__data[index] = value

    def get_value(self, index:Slider):
        return self.__data.get(index)