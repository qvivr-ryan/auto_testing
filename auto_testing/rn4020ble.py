#
#
#

import serial
from time import sleep
#import os

#globals
bleport = None
port = '/dev/ttyUSB0'
baud = 115200
MAC_TO_CONNECT = 'CE58142145F1'
#MAC_TO_CONNECT = '4F9F4E26ABA6'


def ble_scan():
    global bleport
    print('scanning for BLE devices...')
    bleport.write('k\n')
    bleport.write('k\n')
    bleport.write('R,1\n')
    sleep(1)
    bleport.write('SF,1\n')
    sleep(0.5)
    #bleport.write('SR,00000000\n')
    bleport.write('SR,80560000\n')
    sleep(0.5)
    bleport.write('SS,00000000\n')
    #sleep(1)
    bleport.write('R,1\n')
    sleep(5)
    bleport.write('F\n')

def readScan():
    global bleport
    while True:
        if(bleport == None or bleport.isOpen() == False):
            return
        else:
            readLine = bleport.readlines() # attempt to read a character from Serial
        #was anything read?
        if len(readLine) == 0:
            break
        for i in xrange(len(readLine)):
            if 'ERR\r\n' in readLine[i] or 'Reboot\r\n' in readLine[i] or 'AOK\r\n' in readLine[i]:
                continue                
            elif ',' in readLine[i]:
                devices = readLine[i].split(',')
            print devices
            #print 'E,'+devices[1].strip(' "\'')+','+devices[0].strip('"[\'')+'\n'


def ble_connect():
    global bleport
    print('connecting to BLE MAC...'+MAC_TO_CONNECT)
    bleport.write('X\n')
    bleport.readlines() # clear input
    #
    bleport.write('E,1,'+MAC_TO_CONNECT+'\n')

def readConnect():
    global bleport
    while True:
        if(bleport == None or bleport.isOpen() == False):
            return
        else:
            conn_resp = bleport.readlines() # attempt to read a character from Serial
        #was anything read?
        if len(conn_resp) == 0:
            print('exiting')
            break
        print(conn_resp)
        
        if len(conn_resp) > 1:
            if conn_resp[1] == 'Connected\r\n':
                print("Connected !!")
                bleport.write('D\n')
                print('Output of cmd D :\n')
                print(bleport.readlines())
                bleport.write('B,1\n')
                #sleep(1)
                bleport.write('Q,1\n')                
                print('Output of cmd D after B :\n')
                print(bleport.readlines())
                sleep(0.2)
                #bleport.write('PF,6E400001B5A3F393E0A9E50E24DCCA9E\n')
                #sleep(0.2)
                #returnValue2 = bleport.readlines()
                #print(returnValue2)
                #print('done printing PF response\n')
                bleport.write('LC\n')
                sleep(0.2)
                returnValue = bleport.readlines()
                print(returnValue)
                print('done printing LC response\n')
                #6E400003B5A3F393E0A9E50E24DCCA9E
                #6E400002B5A3F393E0A9E50E24DCCA9E
                handle = None
                receive = []
                for line in returnValue:
                    if receive ==[] and '6E400003B5A3F393E0A9E50E24DCCA9E' in line:
                        receive = line.split(",")
                    elif handle == None and '6E400002B5A3F393E0A9E50E24DCCA9E' in line:
                        transmit = line.split(",")
                        if transmit[1]:
                            handle = transmit[1]
                        else:
                            print 'Error in service discovery'
                if receive!= []:
                    bleport.write('CHW,'+ receive[1] +',0100\n')    #Enable read notification
                    sleep(0.2)
                    returnValue = bleport.readlines()
                    print(returnValue)
                    if('ERR\r\n' in returnValue):
                        print 'Error while enabling Read Notification, Device requires bond'
                    #else:
                    #   bt_DFU.config(state='normal')
                if handle:
                    print handle
            elif conn_resp[1] == 'ERR\r\n':
                print "Error in connection... Abort !!"
        else:
            print('Connection not completed..\n')
            print('connection response: '+conn_resp[0])


#open serial port


 
bleport = serial.Serial(port,baud,timeout=1)
sleep(0.5)

bleport.write('V\n') 
returnValue = bleport.readlines()
print(returnValue)

#start scan
ble_scan()
sleep(3)
#check scan report
readScan()
#connect
ble_connect()
#sleep(0.5)
#check connection
readConnect()


bleport.close()


