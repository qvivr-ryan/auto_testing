#!/usr/bin/env python

import pexpect, sys
from sys import platform
from time import sleep

def flashFW(d,jlinkscript='Nordic/flashFW_nordic.jlink'):

    cmdline = "/opt/jlink/JLinkExe -device nrf51822 -if swd -speed 4000 " + jlinkscript
#    cmdline = "jlink -device nrf51822 -if swd -speed 4000 " + jlinkscript
    runresult = pexpect.run(cmdline)
    if any(errstr in runresult.lower() for errstr in ['error', 'failed', 'unknown']):
        print runresult
        print("\n\nError running flash script. See output for details. \n\n")
    else:
        print runresult
        print "\n\nSuccess flashing nrf51!\n\n"
    sleep(d)
    
if __name__ == '__main__':
    if len(sys.argv) == 2:
        flashnrf51(sys.argv[1])
    elif len(sys.argv) == 1:
        flashnrf51()
    else:
        print "Usage:  jlinkflash.py <path_to_jlinkscript>\n  default path: ./Nordic/flash_nordic.jlink\n"

