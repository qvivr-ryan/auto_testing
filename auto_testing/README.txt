To run manually:
ssh into RPi
> ssh 10.1.10.172 -l pi
password: raspberry
> python ~/main.py

output:
logs in ~/logs/
actual file = actual_%Y-%m-%d_%H.%M.%S.txt
expected file = expected_%Y-%m-%d_%H.%M.%S.txt
summary file = summary_%Y-%m-%d_%H.%M.%S.txt

Automated Testing runs every evening at 22:00 from default script "/home/pi/sequences.txt"

sequences format:
INIT:rm,0;start,5;flash,10;ble,0;onboard,10;setlog,2;add1,1;add2,1;delcard1,1;add1,1;add3,1;getlog,2;sel,5;trg_r,1;trg_l,1;getlog,2;p,40

INIT - sequence to run
rm,0 - function call, delay (in s)
       delay is a float
; - separator between function calls

After all test sequences run a summary of the test is emailed. Sample of summary.txt:

INIT: PASSED | ADD1, 1.0, Mom1, PASSED, 69 | ADD2, 1.0, Gift2, PASSED, 4 | DELCARD1, 1.0, Mom1, PASSED, 9 | ADD1, 1.0, Mom1, PASSED, 4 | ADD3, 1.0, loyalty3, PASSED, 6 | SEL, 5.0, PASSED, 11 | TRG_R, 1.0, PASSED, 4 | TRG_L, 1.0, PASSED, 1 |

INIT: PASSED
sequence to run: overall pass/fail

| ADD1, 1.0, Mom1, PASSED, 69 |
| add Mom1 card function, delay before next function, debit card, pass/fail test, timestamp (first is time since power on, following timestamps is delay between function calls) |

Possible logged outputs from testing:
Buttons: UP, SEL, DOWN
Sensors: TRG_L, TRG_R
FW: latest FW version
Adding cards: ADD1/2/3
Deleting cards: DEL (delete all cards), DELCARD1/2/3

Possible functions during a sequence:
START: power on card
P: end of sequence, waits to power off
FLASH: clean flash of latest firmware/bootloader
FLASHFW: flash of latest firmware only (no erase all)
UP, DOWN, SEL: up, down, select (middle) buttons
TRG_L, TRG_R: left and right sensor
BLE: connect card to RPi through bluetooth
RM: remove bonding information of device from bluetooth list of devices
DISCONNECT: disconnect card from RPi (keep bonding information)
## The following need 'BLE' called before seeing expected output ##
FW: get latest FW version
SETLOG: set logging feature
GETLOG: get log of functions, need 'SETLOG' called first
ADD1/2/3: add any of the tree preset cards (1:debit(Mom1), 2:gift(Gift2), 3:loyalty(loyalty3))
DEL: delete all cards
DELCARD1/2/3: delete any of the 3 cards

Wiring:
R3PGMr1
P1                              P2       SEGGER - J200
T2 T1 x TRG_L TRG_R UP SEL DOWN GND 3V   NRF SWD CONNECTOR --> RPi USB
0  1  2 3     4     5  6   7    0   1  
|  |  | |     |     |  |   |    |   |
40 38 x 37    35    29 31  33   39  15
RPi - GPIOs
