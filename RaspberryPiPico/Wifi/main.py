from machine import UART
import machine
import _thread
import time
import wifi

# Define all constants
SSID = "PowerStaack"
PASSWORD = "Staackdasinternet"
TOKEN = ""
DEVICE_LABEL = "test"
VARIABLE_LABEL = "temperature"
USER_AGENT = "randomstring"

# ---------------------- Setup: ------------------------------------------
wifi.setup(SSID, PASSWORD)

sensor_temp = machine.ADC(4)
conversion_factor = 3.3 / (65535)

print("Setup done")

# ---------------------- Loop: --------------------------------------------
while True:
    # temperature reading
    reading_temp = sensor_temp.read_u16() * conversion_factor
    temperature = 27 - (reading_temp - 0.706)/0.001721
    
    state = wifi.is_connected()
    
    if state == "No AP":
        time.sleep(10)
        wifi.connect(SSID, PASSWORD)

    wifi.send_http(temperature, TOKEN, DEVICE_LABEL, VARIABLE_LABEL, USER_AGENT)
    time.sleep(3)

