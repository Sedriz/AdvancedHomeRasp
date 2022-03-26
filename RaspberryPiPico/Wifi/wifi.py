import time
from machine import UART
import machine
import _thread

uart = UART(1, 115200)

print('-- UART Serial --')
print('>', end='')


def uart_serial_rx_monitor(command):
    recv = bytes()
    while uart.any() > 0:
        recv += uart.read(1)
    res = recv.decode('utf-8')
    erase_len = len(command) + 5
    res = res[erase_len:]
    return res


def connect(ssid, password):
    res = ""
    send = "AT+CWJAP=\""+ssid+"\",\""+password+"\""
    uart.write(send+'\r\n')
    time.sleep(7)
    res = uart_serial_rx_monitor(send)
    print("Attempting to connect to WiFi..."+res)
    return res


def is_connected():
    res = ""
    send = "AT+CWJAP?"
    uart.write(send+'\r\n')
    time.sleep(4)
    res = is_connected_response(send)
    if res == "No AP":
        print("WiFi Status:"+res)
    return res


def is_connected_response(command):
    recv = bytes()
    while uart.any() > 0:
        recv += uart.read(1)
    res = recv.decode('utf-8')
    erase_len = len(command)+3
    res = res[erase_len:]
    res = res[:5]
    return res


def send_http(value, token, device_label, variable_label, user_agent):

    send = 'AT+CIPSTART="TCP","industrial.api.ubidots.com",80'
    uart.write(send+'\r\n')
    time.sleep(2)

    # build payload and find its length
    payload = '{"' + variable_label + '":'+str(value)+'}'
    payload_length = len(payload)

    # find request length
    req_length = 147
    req_length += len(device_label + token + str(payload_length) + payload + user_agent)

    send = "AT+CIPSEND="+str(req_length)
    uart.write(send+'\r\n')
    time.sleep(0.6)

    send = "POST /api/v1.6/devices/" + device_label + " HTTP/1.1"
    uart.write(send+'\r\n')
    time.sleep(0.6)

    send = "Host:industrial.api.ubidots.com"
    uart.write(send+'\r\n')
    time.sleep(0.6)

    send = "User-Agent:" + user_agent
    uart.write(send+'\r\n')
    time.sleep(0.6)

    send = "X-Auth-Token:" + token
    uart.write(send+'\r\n')
    time.sleep(0.6)

    send = "Content-Type:application/json"
    uart.write(send+'\r\n')
    time.sleep(0.6)

    send = "Content-Length:"+str(payload_length)
    uart.write(send+'\r\n')
    time.sleep(0.6)

    send = ""
    uart.write(send+'\r\n')
    time.sleep(0.6)

    uart.write(payload+'\r\n')

    send = ""
    uart.write(send+'\r\n')
    time.sleep(0.6)

    print("Data sent: "+payload)


def setup(ssid, password):
    print("Setup Wifi: ")

    connect(ssid, password)
    time.sleep(10)

    send = 'AT+CWMODE=1'
    uart.write(send+'\r\n')
    time.sleep(1)

    send = 'AT+CIPMUX=0'
    uart.write(send+'\r\n')
    time.sleep(1)

    print("Wifi setup done.")
    
