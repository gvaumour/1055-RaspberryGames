import os

#################################
# GAME PARAMETERS

ROOM_ID = 8 # ID used to identify the room by the server

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

DECREMENT_SCORE_PER_SEC = 0
INCREMENT_SCORE_PER_SEC = 5

NB_POLES = 4 # Number of poles in the room

process_server_start = False
process_server_stop = False
current_nb_players = 4

# It defines the parameters for the 3 disturbances planned for the game
# Light OFF, turning on a fan and a stroboscope
# TRIGGER parameter is when the effect is triggered once
# they are correctly set on the poles (in seconds)
# DURATION parameter is how long the effect lasts (in seconds)
FAN_TRIGGER =1
FAN_DURATION = 10

STROBO_TRIGGER = 15
STROBO_DURATION = 10

LIGHT_TRIGGER = 20
LIGHT_DURATION = 10


# Time before re-starting disturbances after a failure (in seconds)
DISTURBANCES_RESTART = 3


color_azur = (33, 163 , 179)
color_lavande = (64, 70 , 153)
color_black = (2, 2 , 2)
red_color = (255, 0 ,0)

bg_color_loose = red_color
bg_color_win = color_azur
bg_color_neutral = color_black

###################################
## Launching configuration to smooth problems between ssh remote connection / windows non compatibility

# For some reason, playing sound from a remote X11 session on raspberry is tricky
SOUND_MANAGEMENT = True # Must be True on production

USING_GPIO = False# Must be True on production

# Use the websocket server to start/stop the game, if not, the game
# is started automatically
USING_WS_SERVER = True #Must be True on production
#################################
