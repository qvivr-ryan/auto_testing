This directory contains the scripts that can be used to automate testing of Swyp card's Firmware.

The testing is done by running BlueZ stack on Raspberry Pi 3 (Model B). 

The instructions for setting up the BLE infrastructure are available in the Evernote Document titled "Raspberry pi BLE dongle connectivity to SWYP card".

testble.py: main script to scan, connect and pair with Swyp card

createbond.py: script to form bond with the peer Swyp card and to use bond information during reconnections

ble_cmd_tx_rx.py: script to form BLE command data packets and send them to the Swyp card and also to process incoming packets

ble_cmd_tlv_parser.py: script to parse incoming TLVs

byte_data_converter.py: logic to convert packet data into values and vice versa