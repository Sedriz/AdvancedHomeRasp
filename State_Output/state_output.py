import argparse
import json
import threading
import time

import paho.mqtt.client as mqtt

# Process arguments
parser = argparse.ArgumentParser()
parser.add_argument('-u', '--username', action='store', dest='username', help='The mqtt username.')
parser.add_argument('-P', '--password', action='store', dest='password', help='The mqtt password.')
parser.add_argument('-id', '--id', type=int, action='store', help='The id you got from Spring boot')
parser.add_argument('-i', '--ip', action='store', dest='ip', default='127.0.0.1', help='The mqtt Server ip')
parser.add_argument('-p', '--port', type=int, action='store', dest='port', default=1883, help='The mqtt Server port')
parser.add_argument('-r', '--pinR', type=int, action='store', default=4, dest='pinR', help='The red pin')
parser.add_argument('-g', '--pinG', type=int, action='store', default=4, dest='pinG', help='The green pin')
parser.add_argument('-b', '--pinB', type=int, action='store', default=4, dest='pinB', help='The blue pin')

args = parser.parse_args()

# ----------------------------------------------------------------------------------------------------------

incomming_topic = f"device/{args.id}/command"

global currentState
currentState = 0
thread = None

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    client.subscribe(incomming_topic)


def on_message(client, userdata, msg):
    payload = str(msg.payload.decode("utf-8"))

    print(msg.topic + ": " + payload)

    data = json.loads(payload)

    if data.get('code') == 'OK':
        isOk()
    elif data.get('code') == 'WARN':
        isWarn()
    elif data.get('code') == 'CLIENT_ERROR':
        isClientError()
    elif data.get('code') == 'SERVER_ERROR':
        isServerError()
    else:
        print('Error')

def isOk():
    global currentState
    if currentState <= 1:
        currentState = 1
        killThread()
        thread = threading.Thread(target=blinkLoop, args=(5, 'g'))
        thread.start()

def isWarn():
    global currentState
    if currentState <= 2:
        currentState = 2
        killThread()
        thread = threading.Thread(target=blinkLoop, args=(10, 'y'))
        thread.start()

def isClientError():
    global currentState
    if currentState <= 3:
        currentState = 3
        killThread()
        thread = threading.Thread(target=blinkLoop, args=(15, 'r'))
        thread.start()

def isServerError():
    global currentState
    currentState = 4
    killThread()
    thread = threading.Thread(target=blinkLoop, args=(20, 'r'))
    thread.start()

def killThread():
    if thread:
        print('Kill tread')
        thread.join()

def blinkLoop(i, color):
    for x in range(i):
        print("Turn on")
        print(color)
        time.sleep(5)
        print("Turn off")
        time.sleep(5)
    currentState = 0
    print('end loop')


# ----------------------------------------------------------------------------------------------------------

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.username_pw_set(username=args.username, password=args.password)
client.connect(args.ip, args.port, 60)

client.loop_forever()