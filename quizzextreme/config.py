import os

################################# 
# GAME PARAMETERS 

ROOM_ID = 17          # ID used to identify the room by the server

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

QUESTIONS_FILE_FR = os.path.join(DIR_PATH,"./assets/questions_fr.txt")
QUESTIONS_FILE_EN = os.path.join(DIR_PATH,"./assets/questions_en.txt")

# French is the language by default 
current_language = "fr"
current_nb_players = 4

# There are 4 buttons, each button is attached to answer A-B-C and D 
NB_BUTTONS = 4

DECREMENT_SCORE = 0
INCREMENT_SCORE = 100

# Time between ground deactivation and play time
WAIT_TIME = 5

process_server_start = False
process_server_stop = False

color_azur = (33, 163 , 179)
color_lavande = (64, 70 , 153)
color_black = (2, 2 , 2, 255)


HEIGHT_REPONSE = 200


################################### 
## Launching configuration to smooth problems between ssh remote connection / windows non compatibility

# For some reason, playing sound from a remote X11 session on raspberry is tricky 
SOUND_MANAGEMENT = True # Must be True on production

# If flag raised, all Windows-specific stuff is not handled such as buttons press and server management
# It allows to test on windows the game
USING_GPIO = True 	    # Must be True on production
USING_WS_SERVER = True  # Must be True on production
################################# 
