import time
import config

if config.USING_GPIO:
	import RPi.GPIO as GPIO

buttons_state = [1 for i in range(config.NB_BUTTONS)]
button_pins = [ 21 , 25 , 26, 13, 20, 16 , 7 , 8 , 2 , 19 ]


# 10 buttons with leds connected directly to Raspberry GPIOs 
def gpio_init():
	if not config.USING_GPIO:
		return

	GPIO.setmode(GPIO.BCM)
	for index in button_pins:
		GPIO.setup(index, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# Return the list of newly pressed buttons
# The index used for buttons is between 0 and NB_BUTTONS
def check_buttons():
	if not config.USING_GPIO:
		return  []

	result = []
	for i in range(len(button_pins)):
		val = GPIO.input(button_pins[i])
		if val != buttons_state[i] and val == 0:
			#print("Button " + str(i) + " is pressed")
			result.append(i)
		buttons_state[i] = val

	return result
