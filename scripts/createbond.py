#!/usr/bin/env python
from __future__ import print_function

from time import sleep
import pexpect

DEVICE_ADD = "CE:58:14:21:45:F1"
ADAPTER_ADD = "B8:27:EB:0B:35:77"

def create_bond(device_address=None, adapter_address=None):
    """Use the 'bluetoothctl' program to create BLE bond.
    """
    con = pexpect.spawn('sudo bluetoothctl')
    con.expect("bluetooth", timeout=1)
    
    print("selecting adapter ...")
    con.sendline("select " + adapter_address.upper())

    #check to see if already paired
    print("checking if bond exists already ...")
    no_bond=False
    try:
        con.sendline("paired-devices")
        con.expect(device_address.upper(), timeout=1)
    except(pexpect.TIMEOUT):
        no_bond = True
    else:
        print("bond already exists for %s" % (device_address.upper()))
        con.sendline("quit") 
        return(0)   
    
    con.sendline("select " + adapter_address.upper())
    
    print("registering agent ...")
    try:
        con.sendline("agent NoInputNoOutput")
        con.expect(['Agent registered', 'Agent is already registered'], timeout=1)
        con.sendline("default-agent")
        con.expect("Default agent request successful", timeout=1)
    except(pexpect.TIMEOUT):
        print("unable to register agent")
        return(1)

    print("enabling pairing ...")
    try:
        con.sendline("pairable on")
        con.expect("Changing pairable on succeeded", timeout=1)
    except(pexpect.TIMEOUT):
        print("unable to turn pairing on")
        return(1)

    print("starting scan ...")
    try:
        con.sendline("scan on")
        devfound = con.expect(device_address.upper(), timeout=5)
        if devfound == 0:
            try:
                con.sendline("scan off")
                print ("Found device. connecting to %s" % (device_address.upper()))
                con.sendline("connect " + device_address.upper())
                con.expect("Connection successful", timeout=10)
                #sleep(10) #need extra time here to finish pairing
            except(pexpect.TIMEOUT):
                print("could not connect to %s" % (device_address.upper()))
                return(1)
            try:
                #explicitly pair with the device
                con.sendline("pair " + device_address.upper())
                con.expect("Pairing successful", timeout=5)
            except(pexpect.TIMEOUT):
                print("pairing not successful")
            try:
                con.sendline("info " + device_address.upper())   
                con.expect("Paired: yes", timeout=1)
            except(pexpect.TIMEOUT):
                print("could not pair with %s" % (device_address.upper()))
                return(1)
            else:
                con.sendline("trust " + device_address.upper())
            print("Connection and pairing successful!")
            #try:
                #con.sendline("list-attributes")
                #con.expect("6e400003-b5a3-f393-e0a9-e50e24dcca9e", timeout=2)
                #print(con.before)
                #for line in con.before:
                #    read_characteristics = line
                #print(read_characteristics)
            #except(pexpect.TIMEOUT):
                #print("could not list the attributes")
                #return(1)
            try:
                print("disconnecting temporarily ...")
                con.sendline("disconnect " + device_address.upper())
                con.expect("Connected: no", timeout=3)
            except(pexpect.TIMEOUT):
                print("could not disconnect.. ")
                con.sendline("quit")
                return(1)
            else:
                con.sendline("quit")
                return(0)
    except(pexpect.TIMEOUT):
        con.sendline("scan off")
        print("unable to find device %s" % (device_address))
        return(1)

