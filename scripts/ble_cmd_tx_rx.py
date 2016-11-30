#!/usr/bin/env python
from __future__ import print_function

import binascii
import pygatt
import time
from binascii import hexlify
from byte_data_converter import shortToBytes, longToBytes, bytesToShortBigEndian, bytesToLongBigEndian
from ble_cmd_tlv_parser import ble_cmd_tlv_parser

MAX_TX_PKT_LEN = 20
uuid_r='6e400003-b5a3-f393-e0a9-e50e24dcca9e'
uuid_w='6e400002-b5a3-f393-e0a9-e50e24dcca9e'
WAIT_FOR_CMD_RESPONSE = 1
CMD_RESPONSE_SUCCESS = 2
CMD_RESPONSE_FAILURE = 3 
pending_cmd_id = 0
pending_cmd_response = WAIT_FOR_CMD_RESPONSE

""" Function to compute crc16 """
def crc16_compute(data):
    crc =  0xffff
    #print("crc16_compute(): size of data is %d\r\n" % (len(data)))
    for c in data:
        msb = crc >> 8
        lsb = crc & 0xff
        crc  = msb | (lsb << 8)
        crc &= 0xffff
        crc ^= c
        crc &= 0xffff
        crc ^= ((crc & 0xff) >> 4)
        crc &= 0xffff
        crc ^= ((crc << 8) << 4)
        crc &= 0xffff
        crc ^= ((crc & 0xff) << 4) << 1;
        crc &= 0xffff

    #print("crc16_compute(): computed crc is 0x%x\r\n" % crc)
    return crc;

""" Generate cmd_id_table """
""" Each entry has the command name and the command id """
BLE_CMD_BASE = 0x400
cmd_id_table = []
cmd_id_table.append(['cmd_none', BLE_CMD_BASE + 0])
cmd_id_table.append(['cmd_version', BLE_CMD_BASE + 1])
cmd_id_table.append(['get_fw_version', BLE_CMD_BASE + 2])
cmd_id_table.append(['add_card', BLE_CMD_BASE + 3])
cmd_id_table.append(['get_log_data', BLE_CMD_BASE + 4])
cmd_id_table.append(['put_log_data', BLE_CMD_BASE + 5])
cmd_id_table.append(['get_mem', BLE_CMD_BASE + 6])
cmd_id_table.append(['set_mem', BLE_CMD_BASE + 7])
cmd_id_table.append(['delete_card', BLE_CMD_BASE + 8])
cmd_id_table.append(['delete_all_cards', BLE_CMD_BASE + 9])
cmd_id_table.append(['get_session_info', BLE_CMD_BASE + 10])
cmd_id_table.append(['put_session_info', BLE_CMD_BASE + 11])
cmd_id_table.append(['backend_auth_1', BLE_CMD_BASE + 12])
cmd_id_table.append(['backend_auth_2', BLE_CMD_BASE + 13])
cmd_id_table.append(['factory_reset', BLE_CMD_BASE + 14])
cmd_id_table.append(['get_card_id', BLE_CMD_BASE + 15])
cmd_id_table.append(['set_card_order', BLE_CMD_BASE + 16])
cmd_id_table.append(['get_card_order', BLE_CMD_BASE + 17])
cmd_id_table.append(['get_atmel_fw_version', BLE_CMD_BASE + 18])
cmd_id_table.append(['atmel_fw_dfu', BLE_CMD_BASE + 19])
cmd_id_table.append(['nordic_fw_dfu', BLE_CMD_BASE + 20])
cmd_id_table.append(['set_logging', BLE_CMD_BASE + 21])
cmd_id_table.append(['get_logging', BLE_CMD_BASE + 22])
cmd_id_table.append(['set_autolock', BLE_CMD_BASE + 23])
cmd_id_table.append(['get_autolock', BLE_CMD_BASE + 24])
cmd_id_table.append(['set_pin', BLE_CMD_BASE + 25])
cmd_id_table.append(['get_pin', BLE_CMD_BASE + 26])
cmd_id_table.append(['set_app_session_info', BLE_CMD_BASE + 27])
cmd_id_table.append(['set_data', BLE_CMD_BASE + 28])
cmd_id_table.append(['cmd_response', BLE_CMD_BASE + 255])

def is_cmd_valid(cmd_id = None):
    for x in cmd_id_table:
        if x[1] == cmd_id:
            #print("is_cmd_valid(): cmd_id = 0x%x is valid\r\n" % cmd_id)
            return True
    print("is_cmd_valid(): cmd_id = 0x%x is invalid\r\n" % cmd_id)
    return False

def get_cmd_id_bytearray(cmd_string):
    for x in cmd_id_table:
        if x[0] == cmd_string:
            return shortToBytes(x[1])

    print("get_cmd_id_array(): cmd not found\r\n")
    return None

def get_cmd_id(cmd_string):
    for x in cmd_id_table:
        if x[0] == cmd_string:
            return x[1]
    print("get_cmd_id_array(): cmd not found\r\n")
    return None


#add_card_payload_1 = bytearray.fromhex("0065 00044d6f 6d310066 0001 01006700 10343432 37343334 30323932 3030 30303100 68000431 38303300 69000330 3031 006d0001 01006b00 41423434 32373433 3430 32393230 30303031 5e474153 5041522f 4d41 52494120 415e3138 30333132 31313030 3030 30303031 30303030 30303836 37303030 3030 303f006c 00263b34 34323734 33343032 3932 30303030 313d3138 30333132 31313030 3030 30303031 3836373f")

############################################################################
# Functions related to forming command payload to send, fragmenting it in  #
# and sending it via BLE MTUs with appropriate command protocol headers    #
############################################################################


"""
Function to send ble cmd packet to the peer 
"""
def ble_cmd_transmit(device=None, cmd=None, cmd_payload=None):
    # declare all the global variables used
    global pending_cmd_id
    global pending_cmd_response
    global ble_command_buffer_status

    """cmd_paylaod is prepended by the cmd header and then split into BLE MTUs to transmit
    cmd_payload is assumed to be a bytearray """
    #print("ble_cmd_transmit(): cmd is %s\r\n" % (cmd))
    cmd_id = get_cmd_id_bytearray(cmd)
    #print("ble_cmd_transmit(): cmd_id is: %s\r\n" % (binascii.hexlify(cmd_id)))
    pending_cmd_id = bytesToShortBigEndian(cmd_id, 0)
    pending_cmd_response = WAIT_FOR_CMD_RESPONSE
    #print(binascii.hexlify(cmd_id))
    cmd_payload_len = len(cmd_payload)
    #print("ble_cmd_transmit(): cmd_payload_len is %d\r\n" % (cmd_payload_len))
    cmd_payload_tx_done_len = 0

    # Mark the receive buffer as free
    ble_command_buffer_status = CMD_BUF_FREE

    """ Create first command packet """
    first_packet = bytearray([])
    first_packet_len = 0
    first_packet.extend(cmd_id)
    first_packet_len += 2
    #print("ble_cmd_transmit(): first_packet is: %s\r\n" % (binascii.hexlify(first_packet)))
    # Create four bytes from the integer
    pkt_seq_no = 0
    pkt_seq_no_bytes = shortToBytes(pkt_seq_no)
    #print(pkt_seq_no_bytes)
    first_packet.extend(pkt_seq_no_bytes)
    first_packet_len += 2
    #print("ble_cmd_transmit(): first_packet is: %s\r\n" % (binascii.hexlify(first_packet)))
    first_packet.extend(longToBytes(crc16_compute(cmd_payload)))
    first_packet_len += 4
    #print("ble_cmd_transmit(): first_packet is: %s\r\n" % (binascii.hexlify(first_packet)))
    first_packet.extend(shortToBytes(cmd_payload_len))
    first_packet_len += 2
    #print("ble_cmd_transmit(): first_packet is: %s\r\n" % (binascii.hexlify(first_packet)))
    if cmd_payload_len == 0:
        #print("ble_cmd_transmit(): first_packet is: %s\r\n" % (binascii.hexlify(first_packet)))
        """ Send the first packet """
        device.char_write(uuid_w,first_packet,wait_for_response=False)
        return
    if cmd_payload_len <= (MAX_TX_PKT_LEN - first_packet_len):
        first_packet.extend(cmd_payload)
        #print("ble_cmd_transmit(): first_packet is: %s\r\n" % (binascii.hexlify(first_packet)))
        cmd_payload_tx_done_len = cmd_payload_len
        """ Send the first packet """
        device.char_write(uuid_w,first_packet,wait_for_response=False)
        return
    else:
        first_packet.extend(cmd_payload[0 : MAX_TX_PKT_LEN - first_packet_len])
        #print("ble_cmd_transmit(): first_packet is: %s\r\n" % (binascii.hexlify(first_packet)))
        cmd_payload_tx_done_len = (MAX_TX_PKT_LEN -first_packet_len)
        """ Send the first packet """
        device.char_write(uuid_w,first_packet,wait_for_response=False)
        
        while (cmd_payload_tx_done_len < cmd_payload_len):
            new_packet = bytearray([])
            new_packet_len = 0
            pkt_seq_no += 1
            pkt_seq_no_bytes = shortToBytes(pkt_seq_no)
            print(pkt_seq_no_bytes)
            new_packet_len += 2
            new_packet.extend(pkt_seq_no_bytes)
            if(cmd_payload_tx_done_len + MAX_TX_PKT_LEN - 2 < cmd_payload_len):
                new_packet.extend(cmd_payload[cmd_payload_tx_done_len : cmd_payload_tx_done_len + MAX_TX_PKT_LEN - new_packet_len])
                #print("ble_cmd_transmit(): new_packet is: %s\r\n" % (binascii.hexlify(new_packet)))
                cmd_payload_tx_done_len += (MAX_TX_PKT_LEN - new_packet_len)
            else:
                new_packet.extend(cmd_payload[cmd_payload_tx_done_len : cmd_payload_len])
                #print("ble_cmd_transmit(): new_packet is: %s\r\n" % (binascii.hexlify(new_packet)))
                cmd_payload_tx_done_len += (cmd_payload_len - cmd_payload_tx_done_len)
            """ Send new packet """
            device.char_write(uuid_w,new_packet,wait_for_response=False)

def ble_cmd_response_status_check(device=None):
    if pending_cmd_response == CMD_RESPONSE_SUCCESS:
        return True
    else:
        return False


############################################################################
# Functions related to handling of received BLE packets, reassembling them #
# and processing the received commands or command responses                #
############################################################################
CMD_BUF_FREE = 0
CMD_BUF_IN_USE = 1
CMD_BUF_FILLED = 2
MAX_PAYLOAD_LENGTH = 512
ble_command_buffer_status = CMD_BUF_FREE

payload_hash = 0
payload_length = 0
packet_seq_no = 0

local_cmd_response_payload = bytearray([])
local_cmd_response_payload_len = 0
local_expected_payload_len = 0

def ble_packet_receive(handle=None, value=None):
    # declare all the global variables used
    global local_cmd_response_payload
    global local_cmd_response_payload_len
    global packet_seq_no
    global payload_hash
    global payload_length
    global pending_cmd_response
    global ble_command_buffer_status
    global pending_cmd_id
    global local_expected_payload_len
    # check the type of the function parameter
    #print("ble_packet_receive(): type of value is %s\r\n" % type(value))
    packet_len = len(value)
    #print("ble_packet_receive(): packet_len = %d\r\n" % packet_len)
    parse_index = 0
    if ble_command_buffer_status == CMD_BUF_FREE:
        rx_cmd_id = bytesToShortBigEndian(value, parse_index)
        if False == is_cmd_valid(rx_cmd_id):
            return
        local_cmd_response_payload = bytearray([])
        local_cmd_response_payload_len = 0
        parse_index += 2
        #print("ble_packet_receive(): rx_cmd_id is %d \r\n" % rx_cmd_id)
        if rx_cmd_id == get_cmd_id('cmd_response'):
            incoming_cmd_id = bytesToShortBigEndian(value, parse_index)
            parse_index += 2
            packet_seq_no = bytesToShortBigEndian(value, parse_index)
            parse_index += 2
            payload_hash = bytesToLongBigEndian(value, parse_index)
            parse_index += 4
            payload_length = bytesToShortBigEndian(value, parse_index)
            parse_index += 2
            cmd_response_status = bytesToShortBigEndian(value, parse_index)
            parse_index += 2
            #print("incoming_cmd_id = 0x%x, packet_seq_no = %d, payload_hash = 0x%x, payload_length = 0x%x, cmd_response_status = %d\r\n" % (incoming_cmd_id, packet_seq_no, payload_hash, payload_length, cmd_response_status))
            local_expected_payload_len = payload_length - 2
            #print("pending_cmd_id = 0x%x\r\n" % pending_cmd_id)
            if pending_cmd_id != incoming_cmd_id :
                #print ("cmd response not for the sent cmd\r\n")
                pending_cmd_response = CMD_RESPONSE_FAILURE
            elif cmd_response_status != 0 :
                #print("cmd response status is not success\r\n")
                pending_cmd_response = CMD_RESPONSE_FAILURE
            else:
                #print("cmd response successfully received\r\n")
                pending_cmd_response = CMD_RESPONSE_SUCCESS
            #pending_cmd_id = 0
        else :
            packet_seq_no = bytesToShortBigEndian(value, parse_index)
            parse_index += 2
            payload_hash = bytesToLongBigEndian(value, parse_index)
            parse_index += 4
            payload_length = bytesToShortBigEndian(value, parse_index)
            parse_index += 2
            print("packet_seq_no = %d, payload_hash = 0x%x, payload_length = 0x%x\r\n" % (packet_seq_no, payload_hash, payload_length))
            local_expected_payload_len = payload_length
            
        if payload_length > MAX_PAYLOAD_LENGTH:
            printf("ble_packet_receive() : payload_length = %d is invalid\r\n" % payload_length)
            return
        else:
            local_cmd_response_payload.extend(value[parse_index:packet_len])
            local_cmd_response_payload_len += (packet_len - parse_index)
            #print("0 local_cmd_response_payload_len = %d, local_cmd_response_payload =0x%s" % (local_cmd_response_payload_len, hexlify(local_cmd_response_payload)))
            ble_command_buffer_status = CMD_BUF_IN_USE
            if local_cmd_response_payload_len >= local_expected_payload_len :
                ble_command_buffer_status = CMD_BUF_FILLED
            
    elif ble_command_buffer_status == CMD_BUF_IN_USE :
        packet_seq_no = bytesToShortBigEndian(value, parse_index)
        parse_index += 2
        local_cmd_response_payload.extend(value[parse_index:packet_len])
        local_cmd_response_payload_len += (packet_len - parse_index)
        #print("1 local_cmd_response_payload_len = %d, local_cmd_response_payload =0x%s" % (local_cmd_response_payload_len, hexlify(local_cmd_response_payload)))
        if local_cmd_response_payload_len >= local_expected_payload_len :
            ble_command_buffer_status = CMD_BUF_FILLED
            
    if ble_command_buffer_status == CMD_BUF_FILLED:
        #print("2 local_cmd_response_payload_len = %d, local_cmd_response_payload =0x%s" % (local_cmd_response_payload_len, hexlify(local_cmd_response_payload)))
        if local_expected_payload_len > 0 :
            ble_cmd_tlv_parser(local_cmd_response_payload)
        ble_command_buffer_status = CMD_BUF_FREE
        pending_cmd_id = 0

    return


#ble_cmd_transmit(None, 'get_fw_version', bytearray([0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10 ]))
