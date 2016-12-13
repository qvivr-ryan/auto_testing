#!/usr/bin/env python

#filename = inputs.py
#author = "Ryan Gaspar"
#date = "December 2, 2016"

import RPi.GPIO as io
import csv,sys,os
from functools import partial
from time import sleep
from time import strftime
from logOutput import *

UP    = 29
SEL   = 31
DOWN  = 33
TRG_L = 35 #15 #35
TRG_R = 37 #13 #37

inputPins = [UP,SEL,DOWN,TRG_L,TRG_R]
btnPins = [UP,SEL,DOWN]
sensorPins = [TRG_L,TRG_R]

POWER_ON_DELAY = 0.020
BUTTON_PRESS_DELAY = 0.030
COIL_FIRE_DELAY = 0.100

DIR = "/home/pi/logs"
e = "expected_" + strftime("%Y-%m-%d_%H.%M.%S") + ".txt"
full_e = os.path.join(DIR,e)
expected = open(full_e,'a+')

logName = "seqLog_" + strftime("%Y-%m-%d_%H.%M.%S") + ".txt"
full_log = os.path.join(DIR,logName)

outputList = []

io.setmode(io.BOARD)

def setup(d):
	print "Powering on..."
#	io.setup(inputPins,io.OUT)
	io.output(btnPins,io.HIGH)
	io.output(sensorPins,io.LOW)
	sleep(d)

def pressLow(pin,d):
#	print "button press"
	io.output(pin,io.LOW)
	sleep(BUTTON_PRESS_DELAY)
	io.output(pin,io.HIGH)
	sleep(d)

def pressHigh(pin,d):
	io.output(pin,io.HIGH)
	sleep(BUTTON_PRESS_DELAY)
	io.output(pin,io.LOW)
	sleep(d)

def triggerSensor(pin,d):
#	print "trigger sensor"
	io.output(pin,io.HIGH)
	sleep(COIL_FIRE_DELAY)
	io.output(pin,io.LOW)
	sleep(d)

def coilFire(pins,d):
	for pin in pins:
		triggerSensor(pins)

#def factoryReset():
#	sleep(5)
#	io.output(DOWN,io.LOW)
#	io.output(UP,io.LOW)
#	sleep(10)
#	io.output(DOWN,io.HIGH)
#	io.output(UP,io.HIGH)
#	sleep(5)
#	pressLow(UP)

def end(startNum,d):
	sleep(d)
	io.output(inputPins,io.LOW)
	print "SEQUENCE " + str(startNum),
	if notFound() : print "FAILED"
	else : print "PASSED"
	expected.close()
	print outputList
	print logList
	seqLog = open(full_log, 'a+')
	seqLog.write(str(startNum) + ": FAILED, ") if notFound() else seqLog.write(str(startNum) + ": PASSED, ")
	## TODO: WRITE TO SEQLOG LIST OF TEST ## seqLog.write(LIST) = [FN,DELAY,ACTUAL,DELAY]
	seqLog.writelines(', '.join(outputList))
	seqLog.write('\n')
	seqLog.close()
	sleep(2)
