#!/usr/bin/env python3

import time

from gpiozero import CPUTemperature
from gpiozero import OutputDevice


def main():
    fan = OutputDevice(18)
    while True:
        cpu = CPUTemperature()
        temperature = cpu.temperature
        print(temperature)
        if  temperature >= 50:
            fan.on()
            print("fan.on()")
        elif temperature <= 45:
            fan.off()
            print("fan.off()")
        time.sleep(1)

if __name__ == '__main__':
    main()