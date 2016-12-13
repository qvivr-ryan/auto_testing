#!/usr/bin/env python

#filename = auto_test_ble_v2.py
#author = "Ryan Gaspar"
#date = "December 2, 2016"

import RPi.GPIO as io
import csv,sys,os
from functools import partial
from time import sleep
from time import strftime

from testble import *
from createbond import *
from inputs import *
from ble_cmd_tlv_parser import *
from jlinkflash import flashnrf51

mydict = {}
filename = "sequences.txt"

io.setmode(io.BOARD)
io.setup(inputPins,io.OUT)

inputDict = {"START":partial(setup),
	     "FLASH":partial(flashnrf51),
	     "BLE":partial(connectBle),
	     "ONBOARD":partial(onboard),
	     "UP":partial(pressLow,pin=UP),
	     "SEL":partial(pressLow,pin=SEL),
	     "DOWN":partial(pressLow,pin=DOWN),
	     "TRG_L":partial(triggerSensor,pin=TRG_L),
	     "TRG_R":partial(triggerSensor,pin=TRG_R),
	     "ADD1":partial(addCard,pl=PAYLOAD1),
	     "ADD2":partial(addCard,pl=PAYLOAD2),
	     "ADD3":partial(addCard,pl=PAYLOAD3),
	     "DEL":partial(delAll),
	     "FW":partial(getFW),
	     "RM":partial(removeBond,d=0),
	     "SETLOG":partial(setLogging),
	     "GETLOG":partial(getLogData),
	     "P":partial(end)}
hwDict = {"UP":log_data_table[4][0],
	  "SEL":log_data_table[5][0],
	  "DOWN":log_data_table[3][0],
	  "TRG_L":log_data_table[12][0]}

def writeToExpected(key,delay):
	expected = open(full_e,'a+')
	##if hwDict.has_key(key) : expected.write(hwDict[key] + '\n')
	##expected.write(hwDict[key] + '\n') if hwDict.has_key(key) else None
	if hwDict.has_key(key):
		expected.write(hwDict[key] + '\n')
		## ADD FN,DELAY TO LIST ##
		outputList.append([key,str(delay)])
#		outputList.append(str(delay))
	expected.close()

def readtable(filename):
	global startNum
	with open(filename,'r') as f:
		for line in f:
			try:
				temp = line.strip().split(":")
				#print [event.split(",") for event in temp[1].split("\t")]
				mydict[temp[0]] = map(lambda item: tuple((str(item[0]),float(item[1]))), [event.split(",") for event in temp[1].split(";")])
			except Exception :
				print("Error reading line: %s" % line)

# readin file and run selected sequences
def runSeq(seq):
	seqlist = mydict.keys() if seq.strip() == '' else seq.strip().split(',')
	for index in seqlist:
		open(full_e, 'a+').write("SEQUENCE " + index + '\n')
		for event in mydict[index]:
			key = event[0].upper()
			delay = event[1]
			print key
			inputDict[key](startNum=index,d=event[1]) if key == "P" else inputDict[key](d=event[1])
			writeToExpected(key,delay)

# user menu for selecting sequences to run
def menu():
	global filename
	global seq
	try:
		##print ("Enter test panel file [%s] :" % filename)
		##s = raw_input().strip()
		##s = filename
		##filename = s if s != '' else None
#		if s != '' : filename = s
		seq = raw_input("Enter sequences to be run separated by commas (If no entry, all sequences will be run) : ")
	except KeyboardInterrupt:
		print "Cancelled by user.. exiting"
		sys.exit(0)

def main():
	try:
		menu()
		readtable(filename)
		runSeq(seq)
	except KeyboardInterrupt:
		print("Cancelled by user... exiting")
		sys.exit(0)
	finally:
		io.output(inputPins,io.LOW)

if __name__ == '__main__':
	main()
