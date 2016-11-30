#!/usr/bin/env python

""" Functions to convert integers/shorts to big endian formatted bytearrays """
def shortToBytes(n):
    b = bytearray([0, 0])   # init
    b[1] = n & 0xFF
    n >>= 8
    b[0] = n & 0xFF    
    return b

def longToBytes(n):
    b = bytearray([0, 0, 0, 0])   # init
    b[3] = n & 0xFF
    n >>= 8
    b[2] = n & 0xFF
    n >>= 8
    b[1] = n & 0xFF
    n >>= 8
    b[0] = n & 0xFF
    return b

def bytesToShortBigEndian(b, index):
    n = 0;
    n = (b[index] << 8) | b[index + 1]    
    return n

def bytesToLongBigEndian(b, index):
    n = 0;
    n = (b[index] << 24) | (b[index + 1] << 16) | (b[index + 2] << 8) | (b[index + 3])    
    return n

