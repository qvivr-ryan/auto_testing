#!/usr/bin/env python
from __future__ import print_function

import sys, os
import binascii
import pygatt
import time
from binascii import hexlify
from byte_data_converter import shortToBytes, longToBytes, bytesToShortBigEndian, bytesToLongBigEndian, bytesToLongLittleEndian
from inputs import *

import globals

DIR = "/home/pi/logs"
r = "actual_" + time.strftime("%Y-%m-%d_%H.%M.%S") + ".txt"
full_r = os.path.join(DIR,r)

#Global TLV IDs
tlv_id_table = []

tlv_id_table.append(['CARD_TAG_TLV_ID', 101])
tlv_id_table.append(['CARD_TYPE_TLV_ID', 102])
tlv_id_table.append(['CARD_NUM_TLV_ID', 103])
tlv_id_table.append(['CARD_EXPIRY_TLV_ID', 104])
tlv_id_table.append(['CARD_CVV_TLV_ID', 105])
tlv_id_table.append(['CARD_GCCODE_TLV_ID', 106])
tlv_id_table.append(['CARD_TRACK_1_TLV_ID', 107])
tlv_id_table.append(['CARD_TRACK_2_TLV_ID', 108])
tlv_id_table.append(['CARD_NW_TYPE_TLV_ID', 109])

tlv_id_table.append(['CARD_BARCODE_TYPE_TLV_ID', 201])
tlv_id_table.append(['CARD_BARCODE_DATA_TLV_ID', 202])

tlv_id_table.append(['CARD_CUSTOM_DISPLAY_1', 301])
tlv_id_table.append(['CARD_CUSTOM_DISPLAY_2', 302])
tlv_id_table.append(['CARD_CUSTOM_DISPLAY_3', 303])

tlv_id_table.append(['LOG_DATA_TLV_ID', 401])
tlv_id_table.append(['MEM_DATA_TLV_ID', 402])
tlv_id_table.append(['FW_VERSION_TLV_ID', 403])
tlv_id_table.append(['FW_TIMESTAMP_TLV_ID', 404])
tlv_id_table.append(['FW_SESSION_TLV_ID', 405])
tlv_id_table.append(['CHALLENGE_REQ_TLV_ID', 406])
tlv_id_table.append(['CHALLENGE_RSP_TLV_ID', 407])
tlv_id_table.append(['FW_CID_TLV_ID', 408])
tlv_id_table.append(['CMD_RSP_STATUS_TLV_ID', 409])
tlv_id_table.append(['GLOBAL_CID_TLV_ID', 410])
tlv_id_table.append(['CARD_ORDER_TLV_ID', 411])
tlv_id_table.append(['CARD_NONCE_TLV_ID', 412])
tlv_id_table.append(['ATMEL_FW_PKT_TLV_ID', 413])
tlv_id_table.append(['ATMEL_FW_SIZE_TLV_ID', 414])
tlv_id_table.append(['BYTE_VALUE_TLV_ID', 415])
tlv_id_table.append(['CARD_PIN_TLV_ID', 416])
tlv_id_table.append(['APP_SESSION_INFO_TLV_ID', 417])
tlv_id_table.append(['DATA_PKT_TLV_ID', 418])
tlv_id_table.append(['DATA_INFO_TLV_ID', 419])
tlv_id_table.append(['IMAGE_PARAMS_TLV_ID', 420])

tlv_id_table.append(['MFG_STAGE_TLV_ID', 501])


def is_tlv_valid(tlv_id = None):
    for x in tlv_id_table:
        if x[1] == tlv_id:
            #print("is_tlv_valid(): tlv_id = 0x%x is valid\r\n" % tlv_id)
            return True
    print("is_tlv_valid(): tlv_id = 0x%x is invalid\r\n" % tlv_id)
    return False

def get_tlv_id(tlv_type = None):
    for x in tlv_id_table:
        if x[0] == tlv_type:
            return x[1]
    return 0

def get_tlv_type(tlv_id = None):
    for x in tlv_id_table:
        if x[1] == tlv_id:
            return x[0]
    return 'None'

def print_tlv_type(tlv_id = None):
    for x in tlv_id_table:
        if x[1] == tlv_id:
            print("TLV Type  : %s\r\n" % x[0])
            return
    print("TLV Type: Invalid (%d)\r\n" % tlv_id)
    

def ble_cmd_tlv_parser (value = None):
    payload_len = len(value)
    remaining_len = payload_len
    parse_index = 0

    while parse_index < (payload_len - 1) :
        #parse for type
        type =  bytesToShortBigEndian(value, parse_index)
        if False == is_tlv_valid(type):
            return
        else :
            print_tlv_type(type)
            parse_index += 2
            
        #parse for length
        length = bytesToShortBigEndian(value, parse_index)
        if length >= remaining_len:
            print("TLV Length: Invalid (%d)\r\n" % length)
            return
        else :
            print("TLV Length: %d\r\n" % length)
            parse_index += 2
            
        #parse for tlv data
        tlv_data = value[parse_index : parse_index + length]
        print("TLV Data  : 0x%s\r\n" % hexlify(tlv_data))
        tlv_intepretor(type, length, tlv_data)
        parse_index += length
        remaining_len -= length
                
    return

def tlv_intepretor (tlv_id = None, tlv_len = None, value = None):
    if(get_tlv_type(tlv_id) == 'FW_VERSION_TLV_ID'):
        print("Firmware version is: %d.%d.%d.%d\r\n" % (value[3], value[2], value[1], value[0]))
    elif(get_tlv_type(tlv_id) == 'FW_CID_TLV_ID'):
        print("Firmware card id is: %d\r\n" % (value[0]))
    elif(get_tlv_type(tlv_id) == 'LOG_DATA_TLV_ID'):
        log_data_interpretor(tlv_len, value)
    elif(get_tlv_type(tlv_id) == 'CHALLENGE_REQ_TLV_ID'):
        globals.card_challenge_received = True
        globals.card_challenge_tlv = value
    else:
        print("tlv_interpretor(): Uninterpretated TLV\r\n")

#Global Log Data IDs
log_data_table = []

log_data_table.append(['log_event_none', 0])
log_data_table.append(['log_event_trigger_left',1])
log_data_table.append(['log_event_trigger_right',2])
log_data_table.append(['log_event_button_left',3])
log_data_table.append(['log_event_button_right',4])
log_data_table.append(['log_event_button_middle',5])
log_data_table.append(['log_event_sys_powerup',6])
log_data_table.append(['log_event_ble_connect',7])
log_data_table.append(['log_event_ble_disconnect',8])
log_data_table.append(['log_event_ble_secured',9])
log_data_table.append(['log_event_pin_secured',10])
log_data_table.append(['log_event_sys_shutoff',11])
log_data_table.append(['log_event_card_swiped',12])
log_data_table.append(['log_event_log_index',13])
log_data_table.append(['log_event_new_bond_success', 14])
log_data_table.append(['log_event_new_bond_fail', 15])
log_data_table.append(['log_event_sw_watchdog_warn', 16])
log_data_table.append(['log_event_app_session_id',17])
log_data_table.append(['log_event_battery_reading',18])
log_data_table.append(['log_event_max',19])

def get_log_event_from_id(id = None):
    for x in log_data_table:
        if x[1] == id:
            return x[0]
    return 'undefined'

def log_data_interpretor(tlv_len = None, value = None):
    global timeDelay
    print("log_data_interpretor(): \r\n")
    i = 0
    results = open(full_r,'a+')
    while i  < tlv_len :
        print("------------------------\r\n")
        print("log event : %s\n" % get_log_event_from_id(value[i]))
        log_event_id = value[i]
	results.write(str(get_log_event_from_id(log_event_id))+", ")
        i += 1
        print("session id: %d\n" % value[i])
        i += 1
        sys.stdout.write("data_1    : %d" % value[i])
        log_data_1_interpretor(log_event_id)
        i += 1
        sys.stdout.write("data_2    : %d" % value[i])
	results.write(str(value[i])+", ")
        log_data_2_interpretor(log_event_id)
        i += 1
        sys.stdout.write("data      : %d" % bytesToLongLittleEndian(value, i))
	results.write(str(value[i])+"\n")
        log_data_3_interpretor(log_event_id)
        i += 4
        #print("i = %d\n" % i)
    results.close() 
    compare(full_e,full_r,full_log,actLine(),expLine(),currLineNum())    

def log_data_1_interpretor(id = None):
    log_event = get_log_event_from_id(id)
    if log_event == 'log_event_trigger_left' or log_event == 'log_event_trigger_right' :
        print(" (bitwidth)\n")
    elif log_event == 'log_event_button_left' or log_event == 'log_event_button_right' or log_event == 'log_event_button_middle' :
        print(" (card FW state)\n")
    elif log_event == 'log_event_sys_powerup' :
        print(" (battery reading (MSB))\n")
    elif log_event == 'log_event_battery_reading' :
        print(" (battery reading (MSB))\n")
    elif log_event == 'log_event_app_session_id' :
        print(" (app session id (MSB))\n")
    elif log_event == 'log_event_card_swiped' :
        print(" (ignore)\n")
    else :
        print(" (card FW state)\n")
        
def log_data_2_interpretor(id = None):
    log_event = get_log_event_from_id(id)
    if log_event == 'log_event_trigger_left' or log_event == 'log_event_trigger_right' :
        print(" (card id)\n")
    elif log_event == 'log_event_button_left' or log_event == 'log_event_button_right' or log_event == 'log_event_button_middle' :
        print("\n")
    elif log_event == 'log_event_sys_powerup' :
        print(" (battery reading (LSB))\n")
    elif log_event == 'log_event_battery_reading' :
        print(" (battery reading (LSB))\n")
    elif log_event == 'log_event_app_session_id' :
        print(" (app session id (LSB))\n")
    else :
        print(" (system timestamp in seconds)\n")
        
def log_data_3_interpretor(id = None):
    log_event = get_log_event_from_id(id)
    if log_event == 'log_event_battery_reading' :
        print(" (battery reading value)\n")
    elif log_event == 'log_event_card_swiped' :
        print(" (last 4 digits of the card swiped)\n")
    elif log_event == 'log_event_sw_watchdog_warn' :
        print(" (ignore)\n")
    else :
        print(" (RTC timestamp counter at 32KHz)\n")
