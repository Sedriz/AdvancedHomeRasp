import argparse
import json
import logging
import os
import configparser
from datetime import datetime

import paho.mqtt.client as mqtt
import psutil
from gpiozero import CPUTemperature
import subprocess


def on_connect(client, userdata, flags, rc):
    logging.info("Connected with result code " + str(rc))

def get_ufw_version():
    ufw_version_b = subprocess.check_output(['sudo', 'ufw', 'version'])
    ufw_version_str = str(ufw_version_b)

    version = ufw_version_str.split("\n")[0]
    if "ufw " in version:
        version_num = version.split("ufw ")[1]
        return str(version_num)
    else:
        return "error"

def get_ufw_status():
    try:
        ufw_status_b = subprocess.check_output(['sudo', 'ufw', 'status'])
        ufw_status_str = str(ufw_status_b)

        version = get_ufw_version()

        ufw_status_obj = {
            "status": "not_reachable",
            "ssh": "inactive",
            "version": version
        }

        if "Status: active" in ufw_status_str:
            ufw_status_obj["status"] = "active"
        elif "Status: inactive" in ufw_status_str:
            ufw_status_obj["status"] = "inactive"

        if "22                         ALLOW       Anywhere" in ufw_status_str:
            ufw_status_obj["ssh"] = "allowed"
        elif "22                        LIMIT       Anywhere" in ufw_status_str:
            ufw_status_obj["ssh"] = "limit"

        return ufw_status_obj
    except:
        logging.error("Error reading UFW status!")
        return  {
            "status": "error",
            "ssh": "error",
            "version": "error"
        }

def get_cpu_temp():
    try:
        cpu = CPUTemperature()
        temperature = cpu.temperature

        if temperature is None:
            raise Exception("No temperature found !")

        return {
            "temperature": temperature,
        }
    except Exception as e:
        logging.error("Error reading Raspi temperature!: " + str(e))
        return {
            "temperature": "error",
        }

def get_raspi_performance():
    try:
        return {
            "cpu": psutil.cpu_percent(4),
            "ram": psutil.virtual_memory()[2],
        }
    except:
        logging.error("Error reading Raspi performance!")
        return {
            "cpu": "error",
            "ram": "error",
        }

def get_root_disc_info():
    try:
        statvfs = os.statvfs('/')

        size_bytes = statvfs.f_frsize * statvfs.f_blocks # Size of filesystem in bytes
        free_bytes = statvfs.f_frsize * statvfs.f_bfree # Actual number of free bytes
        usable_bytes = statvfs.f_frsize * statvfs.f_bavail # Number of free bytes that ordinary users are allowed to use (excl. reserved space)

        return {
            "size": round(size_bytes / 1000000000, 2), # in GB
            "actual_free": round(free_bytes / 1000000000, 2), # in GB
            "can_used_space": round(usable_bytes / 1000000000, 2) # in GB
        }
    except:
        logging.error("Error reading disc!")
        return {
            "size": "error",
            "actual_free": "error",
            "can_used_space": "error",
        }

# Process arguments
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config', action='store', dest='config', help='The location of the config')
parser.add_argument('-id', '--deviceid', action='store', dest='id', default=1, required=False, help='The id of the device')
args = parser.parse_args()

logging.basicConfig(filename="/var/log/rasp_info.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

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

    value = {
        "timestamp": datetime.now().strftime('%m-%d-%YT%H:%M:%S'),
        "cpu": get_cpu_temp(),
        "disc": get_root_disc_info(),
        "performance": get_raspi_performance(),
        "ufw": get_ufw_status()
    }

    jsonValue = json.dumps(value)

    topic = "raspiinfo/" + str(args.id) + "/status"

    logging.info("Publishing to topic: " + topic)

    client.publish(topic, jsonValue)

except:
    logging.error("Error while publishing data to mqtt!")
