import argparse
import json
import logging
import configparser
import random
from datetime import datetime
import time

import paho.mqtt.client as mqtt
from rpi_ws281x import *
from state import State
from mode_enum import ModeEnum


if __name__ == "__main__":
    def connect_mqtt(config, cfg_name) -> mqtt:
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        username = config.get(cfg_name, 'username')
        password = config.get(cfg_name, 'password')
        ip = config.get(cfg_name, 'ip')
        port = config.getint(cfg_name, 'port')
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
            topic = msg.topic

            print(f"Received `{message}` from `{topic}` topic")

            if topic == LED_TOPIC:
                state = State(message)
            elif topic == REQUEST_TOPIC:
                print('Sending state')
                publish(client, state)

        client.subscribe(LED_TOPIC)
        client.subscribe(REQUEST_TOPIC)
        client.on_message = on_message


    def publish(client: mqtt, state_param: State):
        value = state_param.get_json_string()

        logging.info("Publishing to topic: " + PUBLISH_TOPIC)
        logging.info("Publishing message: " + value)

        client.publish(PUBLISH_TOPIC, value)


    def setup_led_stripe(config, cfg_name):
        count = config.getint(cfg_name, 'led_count')
        pin = config.getint(cfg_name, 'led_pin')
        freq_hz = config.getint(cfg_name, 'led_freq_hz')
        dma = config.getint(cfg_name, 'led_dma')
        invert = config.getboolean(cfg_name, 'led_invert')
        brightness = config.getint(cfg_name, 'led_brightness')
        channel = config.getint(cfg_name, 'led_channel')

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


    def execute_mode():
        print("executing")


    args = get_args()
    state: State = State(None)

    # Constants
    LED_TOPIC = f'device/{args.id}/command'
    REQUEST_TOPIC = f'device/{args.id}/request'
    PUBLISH_TOPIC = f'main/{args.id}/1'

    print("Setting up!")

    logging.basicConfig(filename="addressable_led_stripe.log")

    # MQTT config file
    mqtt_config = configparser.ConfigParser()
    mqtt_config.read(args.mqtt_config)
    mqtt_configuration_name = 'mqtt-config'

    # Addressable LED Stripe config file
    led_config = configparser.ConfigParser()
    led_config.read(args.led_config)
    led_configuration_name = 'led-stripe-config'

    # Setup mqtt
    mqtt_client = connect_mqtt(mqtt_config, mqtt_configuration_name)
    subscribe(mqtt_client)
    mqtt_client.loop_start()

    setup_led_stripe(led_config, led_configuration_name)

    print("Setup done!")

    while True:
        try:
            print("hello")

            speed = 1
            if state.speed is not None:
                sleep = state.speed
            time.sleep(speed)

        except:
            logging.error("Error while publishing data to mqtt!")
