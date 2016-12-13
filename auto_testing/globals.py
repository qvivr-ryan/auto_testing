#!/usr/bin/env python

def init():
    global card_challenge_received
    card_challenge_received = False
    global card_challenge_tlv
    card_challenge_tlv = bytearray([])
    global device
    device = None
    
