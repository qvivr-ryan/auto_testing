#!/usr/bin/env python
from __future__ import print_function

import binascii
import pygatt
import time
from binascii import hexlify
from byte_data_converter import shortToBytes, longToBytes, bytesToShortBigEndian, bytesToLongBigEndian

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

def is_tlv_valid(tlv_id = None):
    for x in tlv_id_table:
        if x[1] == tlv_id:
            #print("is_tlv_valid(): tlv_id = 0x%x is valid\r\n" % tlv_id)
            return True
    print("is_tlv_valid(): tlv_id = 0x%x is invalid\r\n" % tlv_id)
    return False


def print_tlv_type(tlv_id = None):
    for x in tlv_id_table:
        if x[1] == tlv_id:
            print("TLV Type : %s\r\n" % x[0])
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
        print("TLV Data : 0x%s\r\n" % hexlify(tlv_data))
        parse_index += length
        remaining_len -= length
                
    return
