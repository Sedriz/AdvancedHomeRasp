import argparse
import json
import logging
import os
import configparser
from datetime import datetime

import paho.mqtt.client as mqtt
import psutil
from gpiozero import CPUTemperature


def on_connect(client, userdata, flags, rc):
    logging.info("Connected with result code " + str(rc))

# Process arguments
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config', action='store', dest='config', help='The location of the config')
parser.add_argument('-id', '--deviceid', action='store', dest='id', help='The id of the device')
parser.add_argument('-n', '--pin', type=int, action='store', default=4, dest='pin', help='The sensor pin')
args = parser.parse_args()

logging.basicConfig(filename="rasp_info.log")

config = configparser.ConfigParser()
config.read(args.config)

configuration_name = 'mqtt-config'

USERNAME = config.get(configuration_name, 'username')
PASSWORD = config.get(configuration_name, 'password')
IP = config.get(configuration_name, 'ip')
PORT = config.getint(configuration_name, 'port')

try:
    client = mqtt.Client()
    client.on_connect = on_connect

    client.username_pw_set(username=USERNAME, password=PASSWORD)
    client.connect(IP, PORT, 60)

    client.loop_start()  # start the loop

    logging.info("Setup done!")

    cpu = CPUTemperature()
    temperature = cpu.temperature

    statvfs = os.statvfs('/')

    if temperature is not None and statvfs is not None:

        value = {
            "timestamp": datetime.now().strftime('%m/%d/%Y'),
            "temperature": temperature,
            "disc": {
                "size": statvfs.f_frsize * statvfs.f_blocks, # Size of filesystem in bytes
                "actual_free": statvfs.f_frsize * statvfs.f_bfree, # Actual number of free bytes
                "can_used_space": statvfs.f_frsize * statvfs.f_bavail # Number of free bytes that ordinary users are allowed to use (excl. reserved space)
            },
            "performance": {
                "cpu": psutil.cpu_percent(4),
                "ram": psutil.virtual_memory()[2],
            }
        }

        jsonValue = json.dumps(value)

        topic = "device/" + args.id + "/command"

        logging.info("Publishing to topic: " + topic)
        logging.info("Publishing message: " + jsonValue)

        client.publish(topic, jsonValue)
    else:
        logging.error("Failed to retrieve data from humidity sensor!")
except:
    logging.error("Error while publishing data to mqtt!")
