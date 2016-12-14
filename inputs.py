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

DIR = "/home/pi/logs"
timestamp = strftime("%Y-%m-%d_%H.%M.%S") + ".txt"
expected_path = os.path.join(DIR,("expected_"+timestamp))
actual_path = os.path.join(DIR,("actual_"+timestamp))
summary_path = os.path.join(DIR,("summary_"+timestamp))

expected_file = open(expected_path,'a+')

outputList = []

actual_start = 1
expected_start = 1

not_found = False
outputList_start = 0
td = 0

def actLine(): return actual_start
def expLine(): return expected_start
def notFound(): return not_found
def currLineNum():
	global outputList_start
	return outputList_start
def resetLineNum():
	global outputList_start
	outputList_start = 0
	return outputList_start

def compare(e,a,actual_current_lineNum,expected_current_lineNum,output_lineNum):
#	global eline,aline,not_found,l,td
	global expected_start,actual_start,not_found,outputList_start,td

	## INIT ##
	expected_file = open(e)
	actual_file = open(a)

	for line in range(actual_current_lineNum):
		actual_current_line = actual_file.readline().strip()
	for line in range(expected_current_lineNum):
		expected_current_line = expected_file.readline().strip()

#	temp = td
#	td = int(str(actual_line).split(',')[1])
	not_found = False

	while expected_current_line != '':
		# if cannot find match before EOF
		if actual_current_line == '':
			not_found = True
			actual_file.close()
			actual_file = open(a)
			for line in range(actual_current_lineNum):
				actual_current_line = actual_file.readline().strip()
		# if match found
		if actual_current_line.find(expected_current_line) != -1:
			temp = td
			outputList[output_lineNum].append(str(actual_current_line).split(',')[0])
			td = int(str(actual_current_line).split(',')[1])
			outputList[output_lineNum].append(str(td-temp))
			actual_current_line = actual_file.readline().strip()
			actual_current_lineNum += 1
			output_lineNum += 1
		else:
			if expected_current_line.find("SEQUENCE") != -1 : pass #lineNum += 1
			else:
				not_found = True
				outputList[output_lineNum].append("FAILED")
				output_lineNum += 1
		expected_current_line = expected_file.readline().strip()
		expected_current_lineNum += 1

	actual_start = actual_current_lineNum
	expected_start = expected_current_lineNum
	outputList_start = output_lineNum

	actual_file.close()
	expected_file.close()

#	actLine()
#	expLine()
#	notFound()

def end(startNum,d):
	global outputList_start,td,actual_start,not_found
	sleep(d)
#	io.output(inputPins,io.LOW)

	actual_file = open(actual_path, 'a+')
	actual_file.write("END OF SEQUENCE " + str(startNum) + ": ")

	print "SEQUENCE " + str(startNum),
	if not_found:#notFound() :
		print "FAILED"
		actual_file.write("FAILED\n")
	else :
		print "PASSED"
		actual_file.write("PASSED\n")
	##print outputList
	
	expected_file.close()
	actual_file.close()

	summary_file = open(summary_path, 'a+')
	summary_file.write(str(startNum) + ": FAILED | ") if not_found else summary_file.write(str(startNum) + ": PASSED | ")
	summary_file.writelines(', '.join(line) + ' | ' for line in outputList)
	summary_file.write('\n')
	summary_file.close()
	sleep(2)

	actual_start += 1
	actLine()

	outputList[:]=[] # clear list
	outputList_start = 0
	td = 0 # clear timestamp
#	resetLineNum() # clear line numbers
#	currLineNum()
