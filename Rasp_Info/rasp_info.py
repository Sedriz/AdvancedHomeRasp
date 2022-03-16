import paho.mqtt.client as mqtt
import argparse
import time
from datetime import datetime
from gpiozero import CPUTemperature
import json
import os


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))


# Process arguments
parser = argparse.ArgumentParser()
parser.add_argument('-u', '--username', action='store', dest='username', help='The mqtt username.')
parser.add_argument('-P', '--password', action='store', dest='password', help='The mqtt password.')
parser.add_argument('-t', '--topic', action='store', dest='topic', help='The mqtt topic to publish to.')
parser.add_argument('-i', '--ip', action='store', dest='ip', default='127.0.0.1', help='The mqtt Server ip')
parser.add_argument('-p', '--port', type=int, action='store', dest='port', default=1883, help='The mqtt Server port')
parser.add_argument('-s', '--seconds', type=float, action='store', dest='seconds', help='The interval to publish')
args = parser.parse_args()

client = mqtt.Client()
client.on_connect = on_connect

client.username_pw_set(username=args.username, password=args.password)
client.connect(args.ip, args.port, 60)

client.loop_start()  # start the loop

while True:
    cpu = CPUTemperature()
    temperature = cpu.temperature

    statvfs = os.statvfs('/home/')

    if temperature != None and statvfs != None:

        value = {
            "timestamp": datetime.now().strftime('%m/%d/%Y'),
            "temperature": temperature,
            "disc": {
                "size": statvfs.f_frsize * statvfs.f_blocks, # Size of filesystem in bytes
                "actual_free": statvfs.f_frsize * statvfs.f_bfree, # Actual number of free bytes
                "can_used_space": statvfs.f_frsize * statvfs.f_bavail # Number of free bytes that ordinary users are allowed to use (excl. reserved space)
            }
        }

        jsonValue = json.dumps(value)

        print("Publishing message to topic", args.topic)

        client.publish(args.topic, jsonValue)
    else:
        print("Failed to retrieve data from humidity sensor")

    time.sleep(args.seconds)  # wait