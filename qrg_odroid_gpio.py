##
#
#	Copyright (c) 2015, Simon Kofler, IN3FQQ
#	
#	Interface fuer die QRG-Steuerung ueber GPIO Ports auf dem ODROID C1
#
#    This file is part of setQRG.
#
#    setQRG is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
## 


import time
import wiringpi2 as wiringpi


### DATA OUT PIN NUMMER
DATA_PIN = 1
### CLK OUT PIN NUMMER	
CLK_PIN = 2
### ENB_RX OUT PIN NUMMER
ENB_RX_PIN = 3
### ENB_TX OUT PIN NUMMER
ENB_TX_PIN = 4
### TX POWER PIN (0: low, 1:high)
PWR_PIN = 5
### ENB-Flag Zeitspanne in Sekunden
ENB_TIME = 0.05
### Taktzeit der seriellen Uebertragung, in Sekunden
CYCLETIME = 0.01



# Initialisiert die wiringpi-Bibliothek und setzt die verwendeten
# Pins in den Output-Mode
def setup():
	wiringpi.wiringPiSetup()
	wiringpi.pinMode(DATA_PIN,1)	# Output fuer DATA
	wiringpi.pinMode(CLK_PIN,1)	# Output fuer CLK
	wiringpi.pinMode(ENB_RX_PIN,1)	# Output fuer ENB_RX
	wiringpi.pinMode(ENB_TX_PIN,1)	# Output fuer ENB_TX
	wiringpi.pinMode(PWR_PIN,1)	# Output fuer PWR_PIN
	wiringpi.digitalWrite(ENB_RX_PIN,0)
	wiringpi.digitalWrite(ENB_TX_PIN,0)
	wiringpi.digitalWrite(CLK_PIN,0)
	wiringpi.digitalWrite(DATA_PIN,0)

#
#	Schiebt ein Bitfeld val seriell aus dem DATA_PIN, MSB Zuerst
#
def sendout(bitfield):
	for i in bitfield:
		wiringpi.digitalWrite(DATA_PIN,i)
		wiringpi.digitalWrite(CLK_PIN,1)
		time.sleep(CYCLETIME)
		wiringpi.digitalWrite(CLK_PIN,0)
		time.sleep(CYCLETIME)
	wiringpi.digitalWrite(DATA_PIN,0) # Am Ende der Uebertragung wird das Bit auf LOW gesetzt

def enableRX():
	wiringpi.digitalWrite(ENB_RX_PIN,1)
	time.sleep(ENB_TIME)	# Halte den HIGH-Pegel am ENB_RX-Pin fuer ENB_TIME Sekunden, kann jedoch aufgrund des Schedulings des Betriebssystems etwas variieren
	wiringpi.digitalWrite(ENB_RX_PIN,0)


def enableTX():
	wiringpi.digitalWrite(ENB_TX_PIN,1)
	time.sleep(ENB_TIME)	# Halte den HIGH-Pegel am ENB_TX-Pin fuer ENB_TIME Sekunden, kann jedoch aufgrund des Schedulings des Betriebssystems etwas variieren
	wiringpi.digitalWrite(ENB_TX_PIN,0)


def setTXPower(pwr):
	wiringpi.digitalWrite(PWR_PIN, pwr)
