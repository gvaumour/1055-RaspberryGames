

DMX is controlled through an arduino Nano 
Check that the serial connection from Raspberry to Arduino Nano is /dev/ttyUSB0

## Arduino Nano Configuration 

To push updates for the Arduino 

Inside the IDE Arduino:
	- Type de Carte -> Arduino Nano
	- Processeur -> ATMega328P (Old Bootloader)

DMX Adresses:
	- Stromboscope: start at DMX address 10 (3 channels + 3)
	- Fan : start at DMX address 50 (3 channels)
