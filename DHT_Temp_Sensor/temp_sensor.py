import paho.mqtt.client as mqtt
import argparse
import Adafruit_DHT
import time
from datetime import datetime
import json
import configparser


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))


# Process arguments
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config', action='store', dest='config', help='The location of the config')
parser.add_argument('-id', '--deviceid', action='store', dest='id', help='The id of the device')
parser.add_argument('-n', '--pin', type=int, action='store', default=4, dest='pin', help='The sensor pin')
args = parser.parse_args()

config = configparser.ConfigParser()
config.read(args.config)

configuration_name = 'mqtt-config'

USERNAME = config.get(configuration_name, 'username')
PASSWORD = config.get(configuration_name, 'password')
IP = config.get(configuration_name, 'ip')
PORT = config.get(configuration_name, 'port')

DHT_SENSOR = Adafruit_DHT.AM2302

client = mqtt.Client()
client.on_connect = on_connect

client.username_pw_set(username=USERNAME, password=PASSWORD)
client.connect(IP, PORT, 60)

client.loop_start()  # start the loop

while True:
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, args.pin)

    if humidity is not None and temperature is not None:
        value = {
            "timestamp": datetime.now().strftime('%m/%d/%Y'),
            "temperature": temperature,
            "humidity": humidity
        }

        jsonValue = json.dumps(value)

        topic = "device/" + args.id + "/command"

        print("Publishing message to topic", topic)

        client.publish(topic, jsonValue)
    else:
        print("Failed to retrieve data from humidity sensor")

    time.sleep(args.seconds)  # wait
