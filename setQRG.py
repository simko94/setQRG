##
#
#	Copyright (c) 2015, Simon Kofler, IN3FQQ
#	
#	QRG-Steuerung fuer Motorola PLL Frequency Synthesizer MC145156
#	im Italtel MB-45
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


import sys
import math
import json
import argparse

##
#
#	Hier kann das verwendete Interface gewechselt werden.
#	Der Alias 'interface' muss jedoch beibehalten werden.
#	Ein gueltiges Interface muss mindestens folgende Funktionen bereitstellen:
#		setup() -	Initialisiere das Interface
#		sendout(bits) -	Sendet eine beliebig lange Liste von Bits
#		enableRX() -	Sendet das ENABLE-Bit fuer den RX-IC
#		enableTX() -	Sendet das ENABLE-Bit fuer den TX-IC
#
##
import qrg_odroid_gpio as interface	# Hier kann das verwendete Interface gewechselt werden

### Datei, in welcher die Parameter abgelegt werden
QRGPARAMS = "/opt/qrgparams"

### Referenzfrequenz des PLL in KHz
REF_PLL = 12.5
### Prescaler, welcher auf dem ITALTEL-Funkgeraet verwendet wird
PRESCALER = 64
### Zwischenfrequenz in KHz
ZF = 21400


# Berechnet den N-Wert fuer eine gegebene Frequenz (QRG) und gegebene PLL-Referenzfrequenz sowie gegebenem Prescaler
def calculateNval(qrg,ref_pll,prescaler):
	return int(math.floor (qrg/ref_pll/prescaler))
	

# Berechnet den A-Wert fuer eine gegebene Frequenz (QRG) und gegebene PLL-Referenzfrequenz sowie gegebenem Prescaler
def calculateAval(qrg,ref_pll,prescaler):
	rest = (qrg/ref_pll/prescaler) - calculateNval(qrg,ref_pll,prescaler)
	return int(rest * prescaler)

# Gibt die binaere Form des uebergebenen Integers als Liste zurueck
# Hierbei werden keine fuehrenden Nullen angegeben
def bitfield(n):
    return [int(digit) for digit in bin(n)[2:]] 

# Gibt die immer 10 Bit lange binaere Form des Integers n zurueck, wobei bei Bedarf 
# fuehrende Nullen hinzugefuegt werden
def bitfield10(n):
	ret = bitfield(n)
	length = len(ret)
	if length < 10:
		for i in range(10-length):
			ret = [0] + ret
	return ret

# Gibt die immer 7 Bit lange binaere Form des Integers n zurueck, wobei bei Bedarf 
# fuehrende Nullen hinzugefuegt werden
def bitfield7(n):
	ret = bitfield(n)
	length = len(ret)
	if length < 7:
		for i in range(7-length):
			ret = [0] + ret
	return ret

##
#
# Hauptprogramm
# 
# Das Skript nimmt zwei Kommandozeilenargumente, RX und TX (Frequenz in KHz!)
# und berechnet die noetigen N- und A-Counter-Bits fuer den MC145156
#
# Das Datenformat sieht folgendermassen aus:
#
#	Serielle Uebertragung, 19 Bit, N und A-Counter werden stets mit dem MSB beginnend seriell uebertragen!
#
#	SW1 | SW2 | N[0] | N[1] | ... | N[9] | A[0] | A[1] | .. | A[6]
#
#
##

# Parameter vom letzten Ausfuehren aus Datei lesen
f = open(QRGPARAMS,"r")
params = json.JSONDecoder().decode(f.read())
f.close()

parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, 
	description='''setQRG - Frequency programming for Motorola MC145156 
	 PLL Frequency Synthesizer

Copyright (C) 2015, Simon Kofler, IN3FQQ
Licence: GPLv3''',prog="setQRG")
parser.add_argument("--tx",help="TX Frequency in kHz")
parser.add_argument("--rx",help="RX Frequency in kHz")
parser.add_argument("--sw1_rx",help="SW1 flag for the RX PLL IC")
parser.add_argument("--sw2_rx",help="SW2 flag for the RX PLL IC")
parser.add_argument("--sw1_tx",help="SW1 flag for the TX PLL IC, currently RF OUTPUT POWER SETTING (1:high, 0:low)")
parser.add_argument("--sw2_tx",help="SW2 flag for the TX PLL IC")
args = vars(parser.parse_args())


##
#
#	Wenn Parameter uebergeben wurden, werden diese natuerlich als neue Werte gesetzt
#	Die uebrigen Werte werden von der QRGPARAMS-Datei uebernommen
#
##

if args["rx"]:
	params["rx"] = args["rx"]
if args["tx"]:
	params["tx"] = args["tx"]
if args["sw1_rx"]:
	params["sw1_rx"] = args["sw1_rx"]
if args["sw2_rx"]:
	params["sw2_rx"] = args["sw2_rx"]
if args["sw1_tx"]:
	params["sw1_tx"] = args["sw1_tx"]
if args["sw2_tx"]:
	params["sw2_tx"] = args["sw2_tx"]
##
#
#	Hier werden die uebergebenen Werte in die benoetigten Datentypen gecastet
#	Dieser Vorgang kann bei falschen Eingaben evtl. zu einem Fehler fuehren.
#	Im Fehlerfall terminiert das Programm sofort mit dem Rueckgabewert 2
#	Dies sollte dann vom Betriebssystem als Fehler erkannt werden und in den Logfiles
#	als fehlerhafte Ausfuehrung des Dienstes protokolliert sein
#
##
try:
	rx = float(params["rx"])
	SWrx = [int(params["sw1_rx"]),int(params["sw2_rx"])]
	tx = float(params["tx"])
	SWtx = [int(params["sw1_tx"]),int(params["sw2_tx"])]
except ValueError:
	print ("Ungueltige werte uebergeben!!")
	sys.exit(2)
print("Setting TX Frequency to",tx)
print("Setting RX Frequency to",rx)
RXnval = calculateNval(rx+ZF,REF_PLL,PRESCALER)
RXaval = calculateAval(rx+ZF,REF_PLL,PRESCALER)
print("Sending RX QRG values to Radio (N:",RXnval,"A:",RXaval,")")
TXnval = calculateNval(tx,REF_PLL,PRESCALER)
TXaval = calculateAval(tx,REF_PLL,PRESCALER)
print("Sending TX QRG values to Radio (N:",TXnval,"A:",TXaval,")")
interface.setup() # Interface starten
# SW1 und SW2 aussenden
print("Setting SW1_RX to",SWrx[0])
print("Setting SW2_RX to",SWrx[1])
interface.sendout(SWrx)
# Nval sind jeweils 10 Bit lang
interface.sendout(bitfield10(RXnval))
# Aval sind jeweils 7 Bit lang
interface.sendout(bitfield7(RXaval))
# Uebertragung abgeschlossen, sende nun das Enable-Signal fuer die RX-QRG
interface.enableRX()
print("Setting SW1_TX to",SWtx[0])
print("Setting SW2_TX to",SWtx[1])
interface.sendout(SWtx)
interface.sendout(bitfield10(TXnval))
interface.sendout(bitfield7(TXaval))
# Uebertragung abgeschlossen, sende nun das Enable-Signal fuer die TX-QRG
interface.enableTX()
# Wenn bis hierher alles ohne fehler durchgegangen ist, wurde die QRG gesetzt
print("Done.")

f = open(QRGPARAMS,"w")
f.write(json.JSONEncoder().encode(params))
f.close()
sys.exit(0)
