#!/usr/bin/env python
from __future__ import print_function

import binascii
#import logging
import pygatt
import time
from time import sleep
from binascii import hexlify
from createbond import create_bond
from createbond import remove_bond
from ble_cmd_tx_rx import ble_cmd_transmit
from ble_cmd_tx_rx import ble_cmd_response_status_check
from ble_cmd_tx_rx import ble_packet_receive
from pygatt.exceptions import NotConnectedError

import globals

#DEVICE_ADD = "CE:58:14:21:45:F1" # Swyp4169
DEVICE_ADD = "E1:51:31:FC:DB:29" # Swyp4119
#DEVICE_ADD = "D0:7E:7D:37:D1:08" # Swyp89
#DEVICE_ADD = "FC:08:AD:FA:63:3A" # Swyp5899
ADAPTER_ADD = "B8:27:EB:0B:35:77"

PAYLOAD1 = "0065 00044d6f 6d310066 0001 01006700 10343432 37343334 30323932 3030 30303100 68000431 38303300 69000330 3031 006d0001 01006b00 41423434 32373433 3430 32393230 30303031 5e474153 5041522f 4d41 52494120 415e3138 30333132 31313030 3030 30303031 30303030 30303836 37303030 3030 303f006c 00263b34 34323734 33343032 3932 30303030 313d3138 30333132 31313030 3030 30303031 3836373f"
PAYLOAD2 = "0065 00054769 66743200 6600 01020067 00103434 32373433 34303239 3230 30303032 00680004 31383033 00690003 3030 32006d00 0101006b 00414234 34323734 3334 30323932 30303030 325e4741 53504152 2f4d 41524941 20415e31 38303331 32313130 3030 30303030 31303030 30303038 36373030 3030 30303f00 6c00263b 34343237 34333430 3239 32303030 30323d31 38303331 32313130 3030 30303030 31383637 3f"
PAYLOAD3 = "0065 00086c6f 79616c74 7933 00660001 03006700 10343432 37343334 3032 39323030 30303300 68000431 38303300 6900 03303033 006d0001 01006b00 41423434 3237 34333430 32393230 30303033 5e474153 5041 522f4d41 52494120 415e3138 30333132 3131 30303030 30303031 30303030 30303836 3730 30303030 303f006c 00263b34 34323734 3334 30323932 30303030 333d3138 30333132 3131 30303030 30303031 3836373f"
SETLOG = "019f 0001 01"
ONBOARDING = "0196 0010 338f 74e4 c792 4f50 6787 8d74 ec09 a973"

# Many devices, e.g. Fitbit, use random addressing - this is required to
# connect.
ADDRESS_TYPE = pygatt.BLEAddressType.random

adapter = pygatt.GATTToolBackend('hci0',None,None)

uuid_r='6e400003-b5a3-f393-e0a9-e50e24dcca9e'
uuid_w='6e400002-b5a3-f393-e0a9-e50e24dcca9e'

data = bytearray([0x04, 0x09, 0x00, 0x00, 0x00, 0x00, 0xff, 0xff, 0x00, 0x00])
data1 = bytearray([0x04, 0x02, 0x00, 0x00, 0x00, 0x00, 0xff, 0xff, 0x00, 0x00])

def cmdresponse(handle=None, value=None):
    #print("Received notification on handle=0x%x, value=0x%s" % (handle, hexlify(value)))
    ble_packet_receive(handle, value)

def connectBle(d):
	try:
	    globals.init()
	    adapter.start()
	    if 0 == create_bond(DEVICE_ADD, ADAPTER_ADD):
	        try:
	            print("Connecting to %s ..." % (DEVICE_ADD))
	            globals.device = adapter.connect(DEVICE_ADD, address_type=ADDRESS_TYPE)
	            time.sleep(10) # needs time to setup connection
	        except NotConnectedError :
	            print("Could not connect to %s. Is the device turned on? " % (DEVICE_ADD))
	            raise NotConnectedError("Fatal error. Could not connect to %s " % (DEVICE_ADD))
	        else:
	            print("Connected to %s" % (DEVICE_ADD))
	    print("discovering services...")
            while True:
                try:
    	            globals.device._characteristics = globals.device.discover_characteristics()
	        except NotConnectedError:
                    print("trying again...")
                    continue
                break   
	    print("done discovering services...")

	    #subscribe for notification
	    print("subscribing to notifications...")
	    globals.device.subscribe(uuid_r, callback=cmdresponse, indication=False)
	   
	    #ready to send/receive data
	    print("ready to send / receive data...\n")

	except NotConnectedError as message:
	    print(message)
	        
	finally:
	    #adapter.stop()
	    print("exiting...")

def disconnectBLE(d): disconnect(DEVICE_ADD, ADAPTER_ADD)

def onboard(d):
	#do_onboarding = raw_input("\n Do you want to do onboarding? (Y/N)")
	#if do_onboarding == 'Y' or do_onboarding == 'y' :
	ble_cmd_transmit(globals.device, 'backend_auth_1', bytearray.fromhex(ONBOARDING))
	sleep(d)

def getFW(d):
	    #raw_input("\npress enter to send cmd: 'get_fw_version' \n")
	    ble_cmd_transmit(globals.device, 'get_fw_version', bytearray([]))
	    #print("time before sleep %s\r\n" % time.ctime())
	    time.sleep(2)
	    #print("time after sleep %s\r\n" % time.ctime())
	    if True == ble_cmd_response_status_check(globals.device):
	        print("get_fw_version cmd successful\r\n")
	    else:
	        print("get_fw_version cmd failed\r\n")
	    time.sleep(d)

def getLogData(d):
	    #raw_input("\npress enter to send cmd: 'get_fw_version' \n")
	    ble_cmd_transmit(globals.device, 'get_log_data', bytearray([]))
	    #print("time before sleep %s\r\n" % time.ctime())
	    time.sleep(2)
	    #print("time after sleep %s\r\n" % time.ctime())
	    if True == ble_cmd_response_status_check(globals.device):
	        print("get_log_data cmd successful\r\n")
	    else:
	        print("get_log_data cmd failed\r\n")
	    time.sleep(d)

def setLogging(d):
	    #raw_input("\npress enter to send cmd: 'get_fw_version' \n")
	    ble_cmd_transmit(globals.device, 'set_logging', bytearray.fromhex(SETLOG))
	    #print("time before sleep %s\r\n" % time.ctime())
	    time.sleep(2)
	    #print("time after sleep %s\r\n" % time.ctime())
	    if True == ble_cmd_response_status_check(globals.device):
	        print("set_logging cmd successful\r\n")
	    else:
	        print("set_logging cmd failed\r\n")
	    time.sleep(d)

def delAll(d):
	    #raw_input("\npress enter to send cmd: 'delete_all_cards' \n")
	    ble_cmd_transmit(globals.device, 'delete_all_cards', bytearray([]))
	    time.sleep(5)
	    if True == ble_cmd_response_status_check(globals.device):
	        print("delete_all_cards cmd successful\r\n")
	    else:
	        print("delete_all_cards cmd failed\r\n")
            time.sleep(d)

def addCard(pl,d):
	    #raw_input("\npress enter to send cmd: 'add_card' \n")
	    #global add_card_payload_1
	    add_card_payload_1 = bytearray.fromhex(pl)
	    ble_cmd_transmit(globals.device, 'add_card', add_card_payload_1)
	    time.sleep(5)
	    if True == ble_cmd_response_status_check(globals.device):
	        print("add_card cmd successful\r\n")
	    else:
	        print("add_card cmd failed\r\n")
            time.sleep(d)

def removeBond(d): remove_bond(DEVICE_ADD, ADAPTER_ADD)

#	    add_card_payload_2 = bytearray.fromhex(PAYLOAD2)
#	    ble_cmd_transmit(device, 'add_card', add_card_payload_2)
#	    time.sleep(5)
#	    if True == ble_cmd_response_status_check(device):
#	        print("add_card cmd successful\r\n")
#	    else:
#	        print("add_card cmd failed\r\n")

#	    add_card_payload_3 = bytearray.fromhex(PAYLOAD3)
#	    ble_cmd_transmit(device, 'add_card', add_card_payload_3)
#	    time.sleep(5)
#	    if True == ble_cmd_response_status_check(device):
#	        print("add_card cmd successful\r\n")
#	    else:
#	        print("add_card cmd failed\r\n")
#	    card_order_payload_1 = bytearray.fromhex("019b 00030001 02")
#	    ble_cmd_transmit(device, 'set_card_order', card_order_payload_1)
#	    time.sleep(2)
#	    if True == ble_cmd_response_status_check(device):
#	        print("set_card_order cmd successful\r\n")
#	    else:
#	        print("set_card_order cmd failed\r\n")
#	    raw_input("\npress enter to exit\n")
#	    

