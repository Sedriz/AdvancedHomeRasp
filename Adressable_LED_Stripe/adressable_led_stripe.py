import argparse
import json
import logging
import configparser
import random
from datetime import datetime

import paho.mqtt.client as mqtt
from rpi_ws281x import *
from state import State


if __name__ == "__main__":
    def connect_mqtt() -> mqtt:
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        client = mqtt.Client(CLIENT_ID)
        client.username_pw_set(USERNAME, PASSWORD)
        client.on_connect = on_connect
        client.connect(IP, PORT)
        return client


    def subscribe(client: mqtt):
        def on_message(client, userdata, msg):
            print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

        client.subscribe(LED_TOPIC)
        client.on_message = on_message


    def publish(client: mqtt, value):
        logging.info("Publishing to topic: " + PUBLISH_TOPIC)
        logging.info("Publishing message: " + value)

        client.publish(PUBLISH_TOPIC, value)


    def setup():
        # Setup mqtt
        client = connect_mqtt()
        subscribe(client)
        client.loop_start()

        print("Setup done!")


    def execute_mode():
        print("executing")


    def deserialize_json(value: str) -> State:
        return State(value)


    def serialize_json(state: State) -> str:
        return json.dumps(state)


    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-mc', '--mqttconfig', action='store', dest='mqtt_config', help='The location of the mqtt config')
    parser.add_argument('-lc', '--ledconfig', action='store', dest='led_config', help='The location of the addressable led config')
    parser.add_argument('-id', '--deviceid', action='store', dest='id', help='The id of the device')
    args = parser.parse_args()

    logging.basicConfig(filename="rasp_info.log")

    # MQTT config file
    mqtt_config = configparser.ConfigParser()
    mqtt_config.read(args.mqtt_config)
    mqtt_configuration_name = 'mqtt-config'

    # Addressable LED Stripe config file
    led_config = configparser.ConfigParser()
    led_config.read(args.led_config)
    led_configuration_name = 'led-stripe-config'

    # Constants
    USERNAME = mqtt_config.get(mqtt_configuration_name, 'username')
    PASSWORD = mqtt_config.get(mqtt_configuration_name, 'password')
    IP = mqtt_config.get(mqtt_configuration_name, 'ip')
    PORT = mqtt_config.getint(mqtt_configuration_name, 'port')
    CLIENT_ID = f'python-mqtt-{random.randint(0, 100)}'
    LED_TOPIC = f'device/{args.id}/command'
    PUBLISH_TOPIC = f'main/{args.id}/1'
    LED_COUNT = led_config.getint(led_configuration_name, 'led_count')
    LED_PIN = led_config.getint(led_configuration_name, 'led_pin')
    LED_FREQ_HZ = led_config.getint(led_configuration_name, 'led_freq_hz')
    LED_DMA = led_config.getint(led_configuration_name, 'led_dma')
    LED_INVERT = led_config.getboolean(led_configuration_name, 'led_invert')
    LED_BRIGHTNESS = led_config.getint(led_configuration_name, 'led_brightness')
    LED_CHANNEL = led_config.getint(led_configuration_name, 'led_channel')

    setup()

    while True:
        try:
            print("hello")
        except:
            logging.error("Error while publishing data to mqtt!")
