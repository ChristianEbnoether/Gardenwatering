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

GPIO.cleanup()

wattersensor_gpio= 6 #watersensor cable
relais4_gpio = 5 #Pump
relais3_gpio = 4 #Ring3
relais2_gpio = 3 #Ring2
relais1_gpio = 2 #Ring1

host = '192.168.1.10'
port = 8086
user = '[user]'
password = '[pw]'
dbname= 'water'
session='garden'


GPIO.setmode(GPIO.BCM) 
GPIO.setwarnings(False) # Ignore warning for now

GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 
GPIO.setup(2, GPIO.OUT)
GPIO.setup(3, GPIO.OUT)
GPIO.setup(4, GPIO.OUT)
GPIO.setup(5, GPIO.OUT)


global wet
wet=False
ring1=False
ring2=False
ring3=False
pump=False
    

def get_sensor_wet():
    global wet    
    for w in range(1):
        if GPIO.input(6) ==True:
            print("wassern (6)")
            wet = False
        if GPIO.input(6) ==False:
            print("kein wassern (6)")
            wet = True

def influx():
    global wet
    global ring1
    global ring2
    global ring3
    global pump
    for t in range(1):

        timestamp=datetime.datetime.utcnow().isoformat()
        datapoints = [
            {
                "measurement": session,
                "time": timestamp,
                "fields": {"wet":wet,"ring1":ring1,"ring2":ring2,"ring3":ring3,"pump":pump}
                }

            ]
        return datapoints

client = InfluxDBClient(host, port, user, password, dbname)





def water_ring1():
    print("Do ring1 now")
    global wet    
    global ring1    
    global pump    
    if wet==False:
        GPIO.output(5, GPIO.HIGH) and GPIO.output(2, GPIO.HIGH)
        r = requests.get("http://[user]:[password]@192.168.97.254/relay/0?turn=on")
        print('Status Code:')
        print(r.status_code)
        ring1=True
        print(f"wet {wet} Pump {pump} and Ring 1 {ring1} Run")
        time.sleep(30)
        GPIO.output(5, GPIO.LOW) and GPIO.output(2, GPIO.LOW)
        print(f"wet {wet} Pump {pump} and Ring 1 {ring1} not Run")
        r = requests.get("http://[user]:[password]@192.168.97.254/relay/0?turn=off")
        print('Status Code:')
        print(r.status_code)
        ring1=False

def water_ring2():
    print("Do ring2 now")
    global wet    
    global ring2    
    global pump    
    if wet==False:
        GPIO.output(5, GPIO.HIGH) and GPIO.output(3, GPIO.HIGH)
        ring2=True
        r = requests.get("http://[user]:[password]@192.168.97.254/relay/0?turn=on")
        print('Status Code:')
        print(r.status_code)
        print(f"wet {wet} Pump {pump} and Ring 2 {ring2} Run")
        time.sleep(30)
        GPIO.output(5, GPIO.LOW) and GPIO.output(3, GPIO.LOW)
        r = requests.get("http://[user]:[password]@192.168.97.254/relay/0?turn=off")
        print('Status Code:')
        print(r.status_code)
        print(f"wet {wet} Pump {pump} and Ring 2 {ring2} Run")
        ring2=False
        
        
        
def water_ring3():
    print("Do ring3 now")
    global wet    
    global ring3    
    global pump    
    if wet==False:
        GPIO.output(5, GPIO.HIGH) and GPIO.output(4, GPIO.HIGH)
        ring3=True
        r = requests.get("http://[user]:[password]@192.168.97.254/relay/0?turn=on")
        print('Status Code:')
        print(r.status_code)
        print(f"wet {wet} Pump {pump} and Ring 3 {ring3} Run")
        time.sleep(30)
        GPIO.output(5, GPIO.LOW) and GPIO.output(4, GPIO.LOW)
        r = requests.get("http://[user]:[password]@192.168.97.254/relay/0?turn=off")
        print('Status Code:')
        print(r.status_code)
        print(f"wet {wet} Pump {pump} and Ring 3 {ring3} Run")
        ring3=False
        
   
schedule.every().day.at("22:58").do(water_ring1)
schedule.every().day.at("19:55").do(water_ring2)
schedule.every().day.at("20:15").do(water_ring3)

while True:
    get_sensor_wet()
    datapoints=influx()
    bResult=client.write_points(datapoints)
    schedule.run_pending()
    time.sleep(1)
