#!/usr/bin/env python

#filename = inputs.py
#author = "Ryan Gaspar"
#date = "December 2, 2016"

import RPi.GPIO as io
import csv,sys,os
from functools import partial
from time import sleep
from time import strftime
#from logOutput import *

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

r = "actual_" + strftime("%Y-%m-%d_%H.%M.%S") + ".txt"
full_r = os.path.join(DIR,r)

outputList = []

io.setmode(io.BOARD)

def setup(d):
	print "Powering on..."
	io.setup(inputPins,io.OUT)
	io.output(btnPins,io.HIGH)
	io.output(sensorPins,io.LOW)

	pressLow(SEL,1)
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

aline = 1
eline = 1

not_found = False
l = 0
td = 0

def actLine(): return aline
def expLine(): return eline
def notFound(): return not_found
def currLineNum():
	global l
	return l
def resetLineNum():
	global l
	l = 0
	return l

def compare(e,a,act_list,exp_list,lineNum):
	global eline,aline,not_found,l,td
	## INIT ##
	expected = open(e)
	actual = open(a)

	for line in range(act_list):
		actual_line = actual.readline().strip()
	for line in range(exp_list):
		expected_line = expected.readline().strip()

#	temp = td
#	td = int(str(actual_line).split(',')[1])
	not_found = False

	while expected_line != '':
		# if cannot find match before EOF
		if actual_line == '':
			not_found = True
			actual.close()
			actual = open(a)
			for line in range(act_list):
				actual_line = actual.readline().strip()
		# if match found
		if actual_line.find(expected_line) != -1:
			temp = td
			outputList[lineNum].append(str(actual_line).split(',')[0])
			td = int(str(actual_line).split(',')[1])
			outputList[lineNum].append(str(td-temp))
			actual_line = actual.readline().strip()
			act_list += 1
			lineNum += 1
		else:
			if expected_line.find("SEQUENCE") != -1 : pass #lineNum += 1
			else:
				not_found = True
				outputList[lineNum].append("FAILED")
				lineNum += 1
		expected_line = expected.readline().strip()
		exp_list += 1

	aline = act_list
	eline = exp_list
	l = lineNum

	actual.close()
	expected.close()

	actLine()
	expLine()
	notFound()
	#currLineNum()

def end(startNum,d):
	global l,td
	sleep(d)
#	io.output(inputPins,io.LOW)

	results = open(full_r, 'a+')
	results.write("END OF SEQUENCE " + str(startNum) + ": ")

	print "SEQUENCE " + str(startNum),
	if notFound() :
		print "FAILED"
		results.write("FAILED\n")
	else :
		print "PASSED"
		results.write("PASSED\n")

	##print outputList
	
	expected.close()
	results.close()

	seqLog = open(full_log, 'a+')
	seqLog.write(str(startNum) + ": FAILED | ") if notFound() else seqLog.write(str(startNum) + ": PASSED | ")
	seqLog.writelines(', '.join(line) + ' | ' for line in outputList)
	seqLog.write('\n')
	seqLog.close()
	sleep(2)

	outputList[:]=[] # clear list
	l = 0
	td = 0 # clear timestamp
	resetLineNum() # clear line numbers
	currLineNum()
