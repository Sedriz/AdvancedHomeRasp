import argparse
import json
import logging
import configparser
import random
from datetime import datetime

import paho.mqtt.client as mqtt
from rpi_ws281x import *
from state import State
from mode_enum import ModeEnum


if __name__ == "__main__":
    def connect_mqtt(mqtt_config, mqtt_configuration_name) -> mqtt:
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        username = mqtt_config.get(mqtt_configuration_name, 'username')
        password = mqtt_config.get(mqtt_configuration_name, 'password')
        ip = mqtt_config.get(mqtt_configuration_name, 'ip')
        port = mqtt_config.getint(mqtt_configuration_name, 'port')
        client_id = f'python-mqtt-{random.randint(0, 100)}'

        client = mqtt.Client(client_id)
        client.username_pw_set(username, password)
        client.on_connect = on_connect
        client.connect(ip, port)
        return client


    def subscribe(client: mqtt):
        def on_message(client, userdata, msg):
            global state
            message = msg.payload.decode()
            print(f"Received `{message}` from `{msg.topic}` topic")
            state = deserialize_json(message)

        client.subscribe(LED_TOPIC)
        client.subscribe(REQUEST_TOPIC)
        client.on_message = on_message


    def publish(client: mqtt, state: State):
        value = serialize_json(state)

        logging.info("Publishing to topic: " + PUBLISH_TOPIC)
        logging.info("Publishing message: " + value)

        client.publish(PUBLISH_TOPIC, value)


    def setup_led_stripe(led_config, led_configuration_name):
        count = led_config.getint(led_configuration_name, 'led_count')
        pin = led_config.getint(led_configuration_name, 'led_pin')
        freq_hz = led_config.getint(led_configuration_name, 'led_freq_hz')
        dma = led_config.getint(led_configuration_name, 'led_dma')
        invert = led_config.getboolean(led_configuration_name, 'led_invert')
        brightness = led_config.getint(led_configuration_name, 'led_brightness')
        channel = led_config.getint(led_configuration_name, 'led_channel')

        # Create NeoPixel object with appropriate configuration.
        strip = Adafruit_NeoPixel(count, pin, freq_hz, dma, invert, brightness, channel)
        # Initialize the library (must be called once before other functions).
        strip.begin()


    def get_args():
        # Process arguments
        parser = argparse.ArgumentParser()
        parser.add_argument('-mc',
                            '--mqttconfig',
                            action='store',
                            dest='mqtt_config',
                            help='The location of the mqtt config')
        parser.add_argument('-lc',
                            '--ledconfig',
                            action='store',
                            dest='led_config',
                            help='The location of the addressable led config')
        parser.add_argument('-id',
                            '--deviceid',
                            action='store',
                            dest='id',
                            help='The id of the device')
        return parser.parse_args()


    def setup(args):
        print("Setting up!")

        logging.basicConfig(filename="rasp_info.log")

        # MQTT config file
        mqtt_config = configparser.ConfigParser()
        mqtt_config.read(args.mqtt_config)
        mqtt_configuration_name = 'mqtt-config'

        # Addressable LED Stripe config file
        led_config = configparser.ConfigParser()
        led_config.read(args.led_config)
        led_configuration_name = 'led-stripe-config'

        # Setup mqtt
        client = connect_mqtt(mqtt_config, mqtt_configuration_name)
        subscribe(client)
        client.loop_start()

        setup_led_stripe(led_config, led_configuration_name)

        print("Setup done!")


    def execute_mode():
        print("executing")


    def deserialize_json(value: str) -> State:
        return State(value)


    def serialize_json(state: State) -> str:
        return json.dumps(state)


    args = get_args()
    state: State

    # Constants
    LED_TOPIC = f'device/{args.id}/command'
    REQUEST_TOPIC = f'device/{args.id}/request'
    PUBLISH_TOPIC = f'main/{args.id}/1'

    setup(args)

    while True:
        try:
            print("hello")
        except:
            logging.error("Error while publishing data to mqtt!")
