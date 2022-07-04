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


wattersensor_gpio= 6 #watersensor cable
relais4_gpio = 5 #Pump
relais3_gpio = 4 #Ring3
relais2_gpio = 3 #Ring2
relais1_gpio = 2 #Ring1



wattersensor_gpio= 6 #watersensor cable
relais4_gpio = 5 #Pump
relais3_gpio = 4 #Ring3
relais2_gpio = 3 #Ring2
relais1_gpio = 2 #Ring1
host = '192.168.1.10'
port = 8086
user = [user]
password = [password]
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
    global ring1    
    global ring2  
    global ring3  
    global pump  
    for w in range(1):
        if GPIO.input(6) ==False:
            print("kein wassern (6)")
            wet = False
            print(f"wet {wet} ")
        if GPIO.input(6) ==True:
            print("wassern (6)")
            wet = True
            print(f"wet {wet} ")

def influx():
    global wet
    global ring1
    global ring2
    global ring3
    global pump
    for t in range(1):

        timestamp=datetime.datetime.utcnow().isoformat()
        print(f"wet {wet} ")
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
        for i in range(300):
            print(i)
            i+=i
            GPIO.output(5, GPIO.HIGH) and GPIO.output(2, GPIO.HIGH)
            print(f"wet {wet} Pump and Ring 1 Run")
            ring1=True
            print(f"ring1 {ring1} ")
            print(f"pump {pump} ")
            print(f"wet {wet} ")
            time.sleep(1)

def water_ring2():
    #print("Do ring2 now")
    global wet    
    global ring2  
    global pump    
    if wet==False:
        GPIO.output(5, GPIO.HIGH) and GPIO.output(3, GPIO.HIGH)
        #print(f"wet {wet} Pump and Ring 3 Run")
        ring1=True
        #print(f"ring2 {ring2} ")
        #print(f"pump {pump} ")
        #print(f"wet {wet} ")
        time.sleep(1)

def water_ring3():
    #print("Do ring3 now")
    global wet    
    global ring3  
    global pump    
    if wet==False:
        GPIO.output(5, GPIO.HIGH) and GPIO.output(4, GPIO.HIGH)
     #   print(f"wet {wet} Pump and Ring 3 Run")
        ring1=True
      #  print(f"ring3 {ring3} ")
      #  print(f"pump {pump} ")
      #  print(f"wet {wet} ")
        time.sleep(1)

schedule.every().day.at("21:59").do(water_ring1)
schedule.every().day.at("19:55").do(water_ring2)
schedule.every().day.at("20:15").do(water_ring3)

while True:
    get_sensor_wet()
    print(f"ring1 {ring1} ")
    #print(f"ring2 {ring2} ")
    #print(f"ring3 {ring3} ")
    print(f"pump {pump} ")
    print(f"wet {wet} ")
    datapoints=influx()
    bResult=client.write_points(datapoints)
    schedule.run_pending()
    time.sleep(1)
