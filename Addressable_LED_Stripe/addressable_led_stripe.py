import argparse
import json
import logging
import configparser
import random
from datetime import datetime
import time

import paho.mqtt.client as mqtt
import board
import neopixel
from state import State
from mode_enum import ModeEnum


if __name__ == "__main__":
    def connect_mqtt(config, cfg_name) -> mqtt:
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                logging.critical(f"{datetime.now()} | Failed to connect, return code {rc}")

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
                state.set_value_from_json(message)
            elif topic == REQUEST_TOPIC:
                print("Sending state")
                publish(client, state)

        client.subscribe(LED_TOPIC)
        client.subscribe(REQUEST_TOPIC)
        client.on_message = on_message


    def publish(client: mqtt, state_param: State):
        value = state_param.get_json_string()

        print("Publishing to topic: " + PUBLISH_TOPIC)
        print("Publishing message: " + value)

        client.publish(PUBLISH_TOPIC, value)


    def setup_led_stripe(count: int) -> neopixel.NeoPixel:
        return neopixel.NeoPixel(board.D18, count, auto_write=True)


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
        parser.add_argument('-c',
                            '--count',
                            action='store',
                            dest='led_count',
                            help='The led count')
        return parser.parse_args()


    def execute_mode():
        mode = state.mode
        if mode is not None:
            if mode == "static":
                static()
            elif mode == "rainbow":
                rainbow()
            elif mode == "stripe":
                stripe()
            elif mode == "gradient":
                gradient()
            elif mode == "blink":
                blink()
            elif mode == "meet":
                meet()
            elif mode == "stars":
                stars()
            elif mode == "swipe_blink":
                swipe_blink()
            else:
                logging.error(f"{datetime.now()} | Mode with name {mode} not found!")


    # ----------------------Modes----------------------------------------------------


    def static():
        print("static")
        if current_led[0] < led_count:
            if len(state.special_numbers) > 0:
                if current_led[0] < state.special_numbers[0]:
                    print("hello")
                    pixels[current_led[0]] = (100, 100, 100)


    def rainbow():
        print("rainbow")


    def stripe():
        print("stripe")


    def gradient():
        print("gradient")


    def blink():
        print("blink")


    def meet():
        print("meet")


    def stars():
        print("stars")


    def swipe_blink():
        print("swipe_blink")


    # ----------------------/Modes----------------------------------------------------

    args = get_args()
    state: State = State(None)
    led_count = 0
    current_led = [0, 0, 0, 0, 0]

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

    pixels: neopixel.NeoPixel = setup_led_stripe(args.led_count)

    print("Setup done!")

    while True:
        try:
            execute_mode()

            speed = 1
            if state.speed is not None:
                speed = state.speed
            time.sleep(speed)

        except:
            logging.error(f"{datetime.now()} | Error while publishing data to mqtt!")
