# setQRG - Setzt Frequenz und Flags von PLL-ICs

setQRG setzt Empfangs- und Sendefrequenz sowie SW1 und SW2 pins eines PLL-ICs.

Der anfängliche Prototyp arbeitet entweder mit einem Dummy-Treiber, der die generierten Daten auf die Standardausgabe schreibt, oder mit einem Treiber für den ODROID-C1 Mikrocomputer.
Dieser benutzt die GPIO-Pins um ein PLL-IC anzusprechen und die werte zu setzen.

Das Programm speichert jeweils die zuletzt eingegebenen Werte JSON-Codiert in einer Textdatei.
Somit müssen bei einem Befehlsaufruf nur die zu ändernden Werte angegeben werden, der Rest wird automatisch aus den gespeicherten Daten gelesen.

Wird das Programm ohne parameter aufgerufen, werden die zuletzt gespeicherten Daten nochmals übertragen.
**Diese Form des Programmaufrufs ist vor allem dafür gedacht, beim Start des Systems ausgeführt zu werden**


# Wählbare Parameter

Das Programm ist aktuell dafür ausgelegt, jeweils 2 PLL-ICs (Rx und Tx) zu beschreiben. Deshalb können insgesamt 6 Werte angegeben werden:

** --rx ** : Empfangsfrequenz
** --tx ** : Sendefrequenz
** --sw1_rx ** : SW1 vom RX-IC
** --sw2_rx ** : SW2 vom RX-IC
** --sw1_tx ** : SW1 vom TX-IC
** --sw2_tx ** : SW2 vom TX-IC

Die Pins, die zur Ansteuerung der Rx und Tx PLL-ICs genutzt werden, werden im jeweiligen Treibermodul angegeben, im jetztigen Fall ist es **qrg_odroid_gpio.py **
