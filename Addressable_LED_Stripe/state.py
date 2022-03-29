import json


class State:
    timestamp = ''
    mode = ''
    speed = 1
    brightness = 80
    colors = []
    special_numbers = []

    def __init__(self, value):
        if type(value) is str:
            self.__dict__ = json.loads(value)
        elif type(value) is object:
            self.timestamp = value.timestamp
            self.mode = value.mode
            self.speed = value.speed
            self.brightness = value.brightness
            self.colors = value.colors
            self.special_numbers = value.special_numbers

    def get_json_string(self) -> str:
        obj = {
            "timestamp": self.timestamp,
            "mode": self.mode,
            "speed": self.speed,
            "brightness": self.brightness,
            "colors": self.colors,
            "special_numbers": self.special_numbers,
        }
        return json.dumps(obj)

    def set_value_from_json(self, value):
        json_obj = json.loads(value)

        self.timestamp = json_obj.timestamp
        self.mode = json_obj.mode
        self.speed = json_obj.speed
        self.brightness = json_obj.brightness
        self.colors = json_obj.colors
        self.special_numbers = json_obj.special_numbers
