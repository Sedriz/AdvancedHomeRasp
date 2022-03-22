# AdvancedHomeRasp
Designed to work with Raspberry PI*

---

## DHT_Temp_Sensor:
### You need:  
- Raspberry Pi
- DHT-Sensor AM2302

### Setup:
###### Setup as Cron-Job:
1. Clone Repo
2. Create new Cron-Job
   1. ````crontab -e````
   2. Add following at the end of the file:
      1. ````*/(MINUTE) * * * * python /home/pi/*FOLDER*/temp_sensor.py -c "../config.cfg" -id <THE DEVICE ID> -n <THE PIN OF THE DHT SENSOR>````

---

## Rasp_Info:
### You need:  
- Raspberry Pi

### Setup:
###### Setup as Cron-Job:
1. Clone Repo
2. Create new Cron-Job
   1. ````crontab -e````
   2. Add following at the end of the file:
      1. ````*/(MINUTE) * * * * python /home/pi/*FOLDER*/Rasp_Info/rasp_info.py -id <THE DEVICE ID>````

---