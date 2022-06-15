import os

################################# 
# GAME PARAMETERS 

ROOM_ID = 2          # ID used to identify the room by the server
ROUND_TIME = 10       # Number of seconds per round 


NB_NOISE_PICTO = 7    # Number of picto displayed on top of the correct one
TOTAL_PICTO = NB_NOISE_PICTO + 1


def convert_difficulty_to_nb_picto(difficulty):
    if difficulty == 2:
        NB_NOISE_PICTO = 11
    elif difficulty == 1:
        NB_NOISE_PICTO = 9
    else :
        NB_NOISE_PICTO = 7
    TOTAL_PICTO = NB_NOISE_PICTO + 1

POINTS_PER_ROUND = 10 # Number of points per good answer

POS_PICTO_X = 0.25    # Ratio for positionning picto X axis 
POS_PICTO_Y = 0.20   # Ratio for positionning picto Y axis 

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

# There are 40 buttons, each picto is attached to 4 buttons:4x10
NB_BUTTONS = 10

# Pictos printed on buttons 
PATH_BUTTONS_PICTO = os.path.realpath(os.path.join(DIR_PATH, "./assets/images/picto_button"))

# Picto not printed on buttons, they are called noise pictos
PATH_NOISE_PICTO = os.path.realpath(os.path.join(DIR_PATH, "./assets/images/picto_noise"))

# Used by the server management 
process_server_start = False
process_server_stop = False
current_nb_players = 4

color_azur = (33, 163 , 179)
color_lavande = (64, 70 , 153)
color_black = (2, 2 , 2, 255)


## Launching configuration to smooth problems between ssh remote connection / windows non compatibility
# For some reason, playing sound from a remote X11 session on raspberry is tricky 
SOUND_MANAGEMENT = True # Must be True on production
USING_WS_SERVER = True 
USING_GPIO = True

################################# 
