#!/usr/bin/python3
# -*- coding: iso-8859-15 -*-

import RPi.GPIO as GPIO
import time
import os
import glob
import argparse
import time
import datetime
import sys
from influxdb import InfluxDBClient
import subprocess
import schedule
import requests


watersensor_gpio= 6 #watersensor cable
relais4_gpio = 5 #Ring3
relais3_gpio = 4 #Ring2
relais2_gpio = 3 #Ring1
relais1_gpio = 1 #Reserve
relais2_3_gpio = 23 #Trafo
relais2_4_gpio = 24 #Pump

host = '192.168.100.9'
port = 8086
user = '[user]'
password = '[password]'
dbname= 'water'
session='garden'


GPIO.setmode(GPIO.BCM) 
GPIO.setwarnings(False) # Ignore warning for now

GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 
GPIO.setup(2, GPIO.OUT)
GPIO.setup(3, GPIO.OUT)
GPIO.setup(4, GPIO.OUT)
GPIO.setup(5, GPIO.OUT)
GPIO.setup(23, GPIO.OUT)
GPIO.setup(24, GPIO.OUT)

GPIO.output(5, GPIO.LOW) and GPIO.output(4, GPIO.LOW) and GPIO.output(3, GPIO.LOW) and GPIO.output(2, GPIO.LOW) and GPIO.output(23, GPIO.LOW) and GPIO.output(24, GPIO.LOW)

global wet
wet=False
ring1=False
ring2=False
ring3=False
pump=False
trafo=False
    

def get_sensor_wet():
    global wet    
    for w in range(1):
        if GPIO.input(6) ==True:
            #print("wassern (6)")
            wet = False
        elif GPIO.input(6) ==False:
            #print("kein wassern (6)")
            wet = True
        else:
            print("else error not /true/not False")
            pass

def influx():
    global wet
    global ring1
    global ring2
    global ring3
    global pump
    global trafo
    for t in range(1):

        timestamp=datetime.datetime.utcnow().isoformat()
        datapoints = [
            {
                "measurement": session,
                "time": timestamp,
                "fields": {"wet":wet,"ring1":ring1,"ring2":ring2,"ring3":ring3,"pump":pump,"trafo":trafo}
                }

            ]
        return datapoints

client = InfluxDBClient(host, port, user, password, dbname)





def water_ring1():
    #Spritzer
    print("Do ring1 now")
    global wet    
    global ring1    
    global pump    
    if wet==False:
        GPIO.setmode(GPIO.BCM)
        GPIO.output(3, GPIO.HIGH) and GPIO.output(2, GPIO.HIGH) and GPIO.output(23, GPIO.HIGH) and GPIO.output(24, GPIO.HIGH)
        #r = requests.get("http://admin:tsgebch1@192.168.97.254/relay/0?turn=on")
        #print('Status Code:')
        #print(r.status_code)
        ring1 = True
        print(f"wet {wet} Pump {pump} and Ring 1 {ring1} Run")
        time.sleep(2)
        GPIO.setmode(GPIO.BCM)
        GPIO.output(3, GPIO.LOW) and GPIO.output(2, GPIO.LOW) and GPIO.output(23, GPIO.LOW) and GPIO.output(24, GPIO.LOW)  
        print(f"wet {wet} Pump {pump} and Ring 1 {ring1} not Run")
        #r = requests.get("http://admin:tsgebch1@192.168.97.254/relay/0?turn=off")
        #print('Status Code:')
        #print(r.status_code)
        ring1 = False
    else:
        pass

def water_ring2():
    #Hecke Nord/Nord-Ost
    print("Do ring2 now")
    global wet    
    global ring2    
    global pump    
    if wet==False:
        GPIO.setmode(GPIO.BCM) 
        GPIO.output(4, GPIO.HIGH) and GPIO.output(2, GPIO.HIGH) and GPIO.output(23, GPIO.HIGH) and GPIO.output(24, GPIO.HIGH)        
        #r = requests.get("http://admin:tsgebch1@192.168.97.254/relay/0?turn=on")
        #print('Status Code:')
        #print(r.status_code)
        ring2 = True
        print(f"wet {wet} Pump {pump} and Ring 2 {ring2} Run")
        time.sleep(2)
        GPIO.setmode(GPIO.BCM) 
        GPIO.output(4, GPIO.LOW) and GPIO.output(2, GPIO.LOW) and GPIO.output(23, GPIO.LOW) and GPIO.output(24, GPIO.LOW) 
        print(f"wet {wet} Pump {pump} and Ring 2 {ring2} not Run")
        #r = requests.get("http://admin:tsgebch1@192.168.97.254/relay/0?turn=off")
        #print('Status Code:')
        #print(r.status_code)
        ring2 = False
    else:
        pass

print(f"wet {wet} \nPump {pump} \nRing 3 {ring3} \nRing 2 {ring2}  \nRing 1 {ring1} \ntrafo {trafo}")        
        
def water_ring3():
    #Rasen
    print("Do ring3 now")
    global wet    
    global ring3    
    global pump    
    if wet==False:
        GPIO.setmode(GPIO.BCM)
        GPIO.output(5, GPIO.HIGH) and GPIO.output(2, GPIO.HIGH) and GPIO.output(23, GPIO.HIGH) and GPIO.output(24, GPIO.HIGH)
        #r = requests.get("http://admin:tsgebch1@192.168.97.254/relay/0?turn=on")
        #print('Status Code:')
        #print(r.status_code)
        print("start ring3")
        ring3 = True
        print(f"wet {wet} Pump {pump} and Ring 3 {ring3} Run")
        time.sleep(240)
        GPIO.setmode(GPIO.BCM)
        GPIO.output(5, GPIO.LOW) and GPIO.output(2, GPIO.LOW) and GPIO.output(23, GPIO.LOW) and GPIO.output(24, GPIO.LOW) 
        print(f"wet {wet} Pump {pump} and Ring 3 {ring3} not Run")
        print("stop ring3")
        #r = requests.get("http://admin:tsgebch1@192.168.97.254/relay/0?turn=off")
        #print('Status Code:')
        #print(r.status_code)
        ring3 = False
    else:
        pass
   
print(f"wet {wet} \nPump {pump} \nRing 3 {ring3} \nRing 2 {ring2}  \nRing 1 {ring1} \ntrafo {trafo}")

#schedule.every().day.at("07:00").do(water_ring1)
schedule.every().day.at("12:36").do(water_ring1)
#schedule.every().day.at("06:55").do(water_ring2)
schedule.every().day.at("12:37").do(water_ring2)
#schedule.every().day.at("07:05").do(water_ring3)
schedule.every().day.at("23:59").do(water_ring3)

while True:
    get_sensor_wet()
    datapoints=influx()

    schedule.run_pending()
    time.sleep(1)
    print(f"wet {wet} \nPump {pump} \nRing 3 {ring3} \nRing 2 {ring2}  \nRing 1 {ring1} \ntrafo {trafo}")
    try:
        client.write_points(datapoints)
    except Exception as exc:
        print(exc)
