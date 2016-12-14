#!/usr/bin/env python

#filename = auto_test_ble_v2.py
#author = "Ryan Gaspar"
#date = "December 2, 2016"

import sys
from jlinkflash import flashnrf51

def main():
	try:
		# load firmware on test bed.
		flashnrf51(jlinkscript='Nordic/flash_nordic.jlink')
		#
	except KeyboardInterrupt:
		print("Cancelled by user... exiting")
		sys.exit(0)

if __name__ == '__main__':
	main()
