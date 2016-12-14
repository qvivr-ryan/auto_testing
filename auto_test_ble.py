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
from jlinkflashFW import flashFW

mydict = {}
filename = "sequences.txt"

io.setmode(io.BOARD)
io.setup(inputPins,io.OUT)

inputDict = {"START":partial(setup),
	     "FLASH":partial(flashnrf51),
             "FLASHFW":partial(flashFW),
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
			if inputDict.has_key(key):inputDict[key](startNum=index,d=event[1]) if key == "P" else inputDict[key](d=event[1])
			writeToExpected(key,delay)
		outputList[:]=[] # clear list after every sequence

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

def randomSequence(filename):
	f = open(filename,'a+')
	head = raw_input("Title of sequence: ")

	for line in f:
		while str(line).split(':')[0] == head:
			print "Title exists!"
			head = raw_input("Title of sequence: ")			

	f.write(head + ":start,10;")
	for item in range(r.randrange(50)):
		key = mydict.keys()[r.randint(0,len(mydict)-1)]
		if key != "START" or "P" : f.write(key + "," + str(round(r.uniform(0.000,10.000),3)))
		f.write(";")
	f.write("trg_l,1;p,45\n")
	f.close()

def addToFile(filename):
	f = open(filename,'a+')
	head = raw_input("Title of sequence: ")

	for line in f:
		while str(line).split(':')[0] == head:
			print "Title exists!"
			head = raw_input("Title of sequence: ")			

	maxItems = raw_input("How many functions for this sequence? ")
	for item in range(int(maxItems)):
		print "\nList of functions:"
		print "START, FLASH, FLASHFW, P(STOP), UP, SEL, DOWN"
		print "BLE, RM, DISCONNECT, SETLOG, GETLOG, ONBOARD"
		print "FW, TRG_L, TRG_R, ADD1, ADD2, ADD3\n"
		print "\nNote: Every sequence ends with TRL_L,1;P,45"

		key = raw_input("Which function do you want to run? ")
		while not mydict.has_key(key.upper()):
			print "Not a listed function."
			key = raw_input("Which function do you want to run? ")
		value = raw_input("What is the delay (min: 0.001s)? ")

		if mydict.has_key(key):f.write(head + ":" + key.upper() + "," + value + ";")

	f.write("trg_l,1;p,45\n")
	f.close()

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
