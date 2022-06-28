#!/usr/bin/python3
from datetime import datetime
import RPi.GPIO as GPIO
import time
import os
import glob
import argparse
import time
import datetime
import sys
from influxdb import InfluxDBClient
import RPi.GPIO as GPIO
import subprocess
from machine import Pin


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


os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

GPIO.setmode(GPIO.BCM) 
GPIO.setwarnings(False)

count_work=0

# Initialisierung von GPIO25 als Ausgang
pump_onboard = Pin(5, Pin.OUT, value=0)

# Initialisierung von GPIO6 als Eingang
btn = Pin(6, Pin.IN, Pin.PULL_DOWN)

# Taster-Funktion
def on_pressed(timer):
    pump_onboard.toggle()
    print('pressed')

# Taster-Auslösung
btn.irq(trigger=Pin.IRQ_RISING, handler=on_pressed)

#print(count_work)
def get_temp():
    global count_dont
    global count_work
    
    temp_Dach=0
    temp_Luft=0
    temp_Nachlauf=0
    temp_Vorlauf=0

    for t in range(1):

        tempfile_Luft = open(Luft)
        text_Luft = tempfile_Luft.read() 
        tempfile_Luft.close() 
        tline_Luft = text_Luft.split("\n")[1] # the second line contains temperature
        tdata_Luft = tline_Luft.split(" ")[9] # position 9 contains temparature value
        temp_Luft  += float(tdata_Luft[2:])/1000
        temp_Delta=temp_Dach-temp_Vorlauf
   

        if (temp_Dach-temp_Vorlauf > temp_Soll):
            GPIO.setmode(GPIO.BCM) # GPIO Numbers instead of board numbers
            GPIO.setwarnings(False)
            RELAIS_1_GPIO = 21
            GPIO.setup(RELAIS_1_GPIO, GPIO.OUT) # GPIO Assign mode
            GPIO.output(RELAIS_1_GPIO, GPIO.HIGH) # out
            time.sleep(60)
            count_work +=1

    
        if (temp_Dach-temp_Vorlauf < temp_Soll):
            GPIO.setmode(GPIO.BCM) # GPIO Numbers instead of board numbers
            GPIO.setwarnings(False)
            RELAIS_1_GPIO = 21
            GPIO.setup(RELAIS_1_GPIO, GPIO.OUT) # GPIO Assign mode
            GPIO.output(RELAIS_1_GPIO, GPIO.LOW) # out
            time.sleep(60)
            count_dont +=1
    


        else:
            time.sleep(5)

        timestamp=datetime.datetime.utcnow().isoformat()
        datapoints = [
            {
                "measurement": session,
                "time": timestamp,
                "fields": {"temp_Dach":temp_Dach,"temp_Vorlauf":temp_Vorlauf,"temp_Nachlauf":temp_Nachlauf,"temp_Luft":temp_Luft,"temp_Delta":temp_Delta,"count_work":count_work,"count_dont":count_dont}
            }

            ]
        return datapoints
    


    else: 
        return (temp_Dach / 1000)

client = InfluxDBClient(host, port, user, password, dbname)

def clear_counter():
    today = datetime.date.today()
    now=(round(time.time() - time.mktime(today.timetuple())))
    if now> 86200 :
        global count_work
        global count_dont
        count_work=0
        count_dont=0
#        print(now)



while True:
    datapoints=get_temp()
    bResult=client.write_points(datapoints)
    #time.sleep(10)
#    clear_counter()
    # Create Influxdb datapoints (using lineprotocol as of Influxdb >1.1)
#    print("Write points {0} bResult:{0}".format(datapoints,bResult))
# Initialize the Influxdb client

#        # Write datapoints to InfluxDB
#print(count_work)
#print(count_dont)
#time.sleep(2) 


# #!/usr/bin/python
##encoding:utf-8

#import RPi.GPIO as GPIO                    #Import GPIO library
#import time                                #Import time library
#GPIO.setmode(GPIO.BCM)                     #Set GPIO pin numbering 

#TRIG = 15                                  #Associate pin 15 to TRIG
#ECHO = 14                                  #Associate pin 14 to Echo

#print "Distance measurement in progress"

#GPIO.setup(TRIG,GPIO.OUT)                  #Set pin as GPIO out
#GPIO.setup(ECHO,GPIO.IN)                   #Set pin as GPIO in

#while True:

 # GPIO.output(TRIG, False)                 #Set TRIG as LOW
 # print "Waiting For Sensor To Settle"
 # time.sleep(2)                            #Delay of 2 seconds

  #GPIO.output(TRIG, True)                  #Set TRIG as HIGH
  #time.sleep(0.00001)                      #Delay of 0.00001 seconds
  #GPIO.output(TRIG, False)                 #Set TRIG as LOW

  #while GPIO.input(ECHO)==0:               #Check if Echo is LOW
   # pulse_start = time.time()              #Time of the last  LOW pulse

  #while GPIO.input(ECHO)==1:               #Check whether Echo is HIGH
   # pulse_end = time.time()                #Time of the last HIGH pulse 

  #pulse_duration = pulse_end - pulse_start #pulse duration to a variable

  #distance = pulse_duration * 17150        #Calculate distance
  #distance = round(distance, 2)            #Round to two decimal points

  #if distance > 20 and distance < 400:     #Is distance within range
   # print "Distance:",distance - 0.5,"cm"  #Distance with calibration
  #else:
   # print "Out Of Range"                   #display out of range

