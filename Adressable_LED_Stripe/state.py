import json


class State:
    timestamp = ''
    mode = ''
    speed = 100
    brightness = 80
    colors = []
    special_numbers = []

    # def __init__(self, mode, colors, special_numbers):
    #     self.mode = mode
    #     self.colors = colors
    #     self.special_numbers = special_numbers

    def __init__(self, value):
        self.__dict__ = json.loads(value)
