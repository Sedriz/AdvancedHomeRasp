import json


class State:
    timestamp = ''
    mode = ''
    speed = 100
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
        return json.dumps(self)
