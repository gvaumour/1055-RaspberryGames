import config

if config.USING_GPIO:
	import RPi.GPIO as GPIO
	ser = serial.Serial("/dev/ttyUSB0", 9600, timeout = 2)


buttons_state = [1 for i in range(config.NB_BUTTONS)]
button_pins = [14 , 19 , 0, 26]

ground_detection_pin = 22

ground_detection_pin = 5

# Adresses of I2C components: 0, 1 and 2
def gpio_init():
	if not config.USING_GPIO:
		return

	assert(config.NB_BUTTONS == len(button_pins))

	GPIO.setmode(GPIO.BCM)
	for index in button_pins:
		GPIO.setup(index, GPIO.IN, pull_up_down=GPIO.PUD_UP)

	GPIO.setup(ground_detection_pin , GPIO.IN , pull_up_down = GPIO.PUD_UP)
	
# Return the list of newly pressed buttons
# The index used for buttons is between 0 and NB_BUTTONS
def check_button_press():
	if not config.USING_GPIO:
		return  []

	result = []
	for i in range(len(button_pins)):
		val = GPIO.input(button_pins[i])
		if val != buttons_state[i] and val == 0:
			print("Button " + str(i) + " is pressed")
			result.append(i)
		buttons_state[i] = val

	return result

def is_ground_detection_activated():
	val = GPIO.input(ground_detection_pin)
	return val == 0

def is_lidar_activated():
    if config.USING_GPIO:
        ser.write("is_activated".encode())
        ser.flush()
        return ser.readline() == "yes"

