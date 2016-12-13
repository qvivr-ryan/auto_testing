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

aline = 1
eline = 1

not_found = False
l = 0

def actLine(): return aline
def expLine(): return eline
def notFound(): return not_found
def currLineNum(): return l

def compare(e,a,s,act_list,exp_list,lineNum):
	global eline,aline,not_found,l

	expected = open(e)
	actual = open(a)
#	seqLog = open(s, 'a+')

	for line in range(act_list):
		actual_line = actual.readline().strip()
	for line in range(exp_list):
		expected_line = expected.readline().strip()

#	temp = int(str(actual_line).split(',')[1])
	td = 0
	lineNum = 0

	while expected_line != '':
		# if cannot find match before EOF
		if actual_line == '':
			actual.close()
			actual = open(a)
			for line in range(act_list):
				actual_line = actual.readline().strip()
		# if match found
		if actual_line.find(expected_line) != -1:
#			seqLog.write("Expected line %d matches actual line %d! " % (exp_list,act_list) + expected_line + " > " + actual_line + '\n')
			temp = td
			outputList[lineNum].append(str(actual_line).split(',')[0])
#			if str(actual_line).split(',')[0] == 'log_event_card_swiped' : td = int(str(actual_line).split(',')[2])
#			else : td = int(str(actual_line).split(',')[1])
			td = int(str(actual_line).split(',')[1])
			outputList[lineNum].append(str(td-temp))
			actual_line = actual.readline().strip()
			act_list += 1
			lineNum += 1
		else:
			if expected_line.find("SEQUENCE") != -1 : pass #lineNum += 1
			else:
#				seqLog.write("Line %d not found during actual test. " % exp_list + expected_line + '\n')
				not_found = True
				outputList[lineNum].append("FAILED")
				lineNum += 1
#		if expected_line.find("SEQUENCE") != -1 : lineNum += 1
#		else : outputList[lineNum-1].append(expected_line)
		expected_line = expected.readline().strip()
		exp_list += 1

	aline = act_list
	eline = exp_list
###	l = lineNum

	actual.close()
	expected.close()
#	seqLog.close()

	actLine()
	expLine()
	notFound()
####	currLineNum()

def end(startNum,d):
	sleep(d)
	io.output(inputPins,io.LOW)

	print "SEQUENCE " + str(startNum),
	if notFound() : print "FAILED"
	else : print "PASSED"

#	print outputList
	expected.close()

	seqLog = open(full_log, 'a+')
	seqLog.write(str(startNum) + ": FAILED | ") if notFound() else seqLog.write(str(startNum) + ": PASSED | ")
	seqLog.writelines(', '.join(line) + ' | ' for line in outputList)
	seqLog.write('\n')
	seqLog.close()
	sleep(2)
	outputList[:]=[] # clear list
