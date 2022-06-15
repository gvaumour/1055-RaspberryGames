import config
import serial 
import time 

if config.USING_GPIO:
    import RPi.GPIO as GPIO


poles_pins = [18, 23 , 16, 20]
floor_detection_pin = 21
room_lights_relay = 14


# For stromboscope and fans, they are connected through DMX to an arduino nano 
# The raspberry communicates through Serial to arduino nano to start/stop the DMX components

if config.USING_GPIO:
    ser = serial.Serial("/dev/ttyUSB0", 9600, timeout = 2);

def gpio_init():
    if not config.USING_GPIO:
        return

    assert(config.NB_POLES == len(poles_pins))

    GPIO.setmode(GPIO.BCM)
    for index in poles_pins:
        GPIO.setup(index, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    GPIO.setup(floor_detection_pin, GPIO.IN , pull_up_down=GPIO.PUD_UP)
    GPIO.setup(room_lights_relay, GPIO.OUT)
    activate_relay()

# Return the list of poles with activated switches
def nb_people_detected():
    if not config.USING_GPIO:
        return 2

    result = 0
    for i in range(len(poles_pins)):
        val = GPIO.input(poles_pins[i])
        if val == 0:
            result = result + 1
    return result
    #return 4

def is_floor_activated():
    if not config.USING_GPIO:
        return False
    #return GPIO.input(floor_detection_pin) == 0
    return False

def send_dmx_request(request):
    if config.USING_GPIO:
        ser.write(request.encode())
        ser.flush()
        while ser.readline() != "ok":
            ser.write(request.encode())
            ser.flush()
            

def activate_strombo():
    send_dmx_request("strombo_on")
def deactivate_strombo():
    send_dmx_request("strombo_off")
def activate_fan():
    send_dmx_request("fan_on")
def deactivate_fan():
    send_dmx_request("fan_off")

def deactivate_relay():
    if config.USING_GPIO:
        GPIO.output(room_lights_relay, GPIO.HIGH)

def activate_relay():
    if config.USING_GPIO:
        GPIO.output(room_lights_relay, GPIO.LOW)

