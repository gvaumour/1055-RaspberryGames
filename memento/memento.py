#!/usr/bin/env python

import os
import sys
import pyglet
import random
import logging

import config 

if config.USING_WS_SERVER:
    sys.path.insert(0,os.path.realpath(os.path.join(config.DIR_PATH,"../common")))
    import server_management

import gpio_management


window = pyglet.window.Window(fullscreen=True)

picto_position = []
for i in range(4):
    for j in range(3):
        picto_position.append([window.width*0.2*(i+1), window.height*0.2 + window.height*0.2*j])

loose_sound_player = pyglet.media.Player()
win_sound_player = pyglet.media.Player()

def handle_win():
    global win_sound_player

    # Playing win sound effect 
    if config.SOUND_MANAGEMENT:
        if win_sound_player.playing:
            win_sound_player.pause()
            win_sound_player.next_source()
        win_sound_player = win_sound.play()
    score.increment_score()
    board.increase_difficulty()
    timer.reset_timer()
    board.do_next_round()


def handle_loose():
    global loose_sound_player
    # Playing loose sound effect 
    if config.SOUND_MANAGEMENT:
        if loose_sound_player.playing:
            loose_sound_player.pause()
            loose_sound_player.next_source()
        loose_sound_player = loose_sound.play()
    board.decrease_difficulty()
    timer.reset_timer()
    board.do_next_round()


def check_raspi_buttons(dt):
    if not game_state_running:
        return
 
    buttons_pressed = gpio_management.check_buttons()
    if len(buttons_pressed) > 0:
    
        #print(buttons_pressed)
        if board.verify_answer(buttons_pressed):
            handle_win()
        else:    
            handle_loose()

def isCorrectPicto(picto_path):
    # To be improved with other criteria 
    if os.path.isfile(picto_path):
        return True

def resize_image(image, array):
    width = 600

    image.anchor_x = image.width // 2
    image.anchor_y = image.height // 2
    image_sprite = pyglet.sprite.Sprite(image, x=window.width//2, y = window.height//2)
    image_sprite.scale = width / window.width
    array.append(image_sprite)

def resize_images():
    for image in img_buttons_picto:
        resize_image(image, sprite_buttons_picto)
    for image in img_noise_picto:
        resize_image(image, sprite_noise_picto)


def process_server_command(_):

    global game_score, game_state_running, timer
    
    if config.process_server_stop:
        if not game_state_running: 
            logging.warning("Attempting to stop a game already stopped ??")
        timer.running = False
        timer.stop_timer()
        server_management.send_request_score(game_score)
        game_state_running = False
        config.process_server_stop = False
    
    if config.process_server_start:
        if game_state_running: 
            logging.warning("Attempting to start a game already started")
        timer.reset_timer()
        timer.running = True
        game_state_running = True
        config.process_server_start = False
        board.difficulty = 0

class Board:
    def __init__(self):
        self.difficulty = 2
        config.convert_difficulty_to_nb_picto(self.difficulty)
        self.do_next_round()


    def increase_difficulty(self):
        self.difficulty += 1
        config.convert_difficulty_to_nb_picto(self.difficulty)

    def decrease_difficulty(self):
        self.difficulty -= 1
        config.convert_difficulty_to_nb_picto(self.difficulty)

    def do_next_round(self):

        self.displayed_noise_picto = random.sample(sprite_noise_picto, k = config.NB_NOISE_PICTO)
        self.displayed_button_picto = random.sample(sprite_buttons_picto, k = 1)[0]

        list_of_position = random.sample(range(len(picto_position)), config.TOTAL_PICTO)
        index = 0
        for pos in list_of_position: 
            if index == config.TOTAL_PICTO-1:
                self.displayed_button_picto.x = picto_position[pos][0] + random.randint(-70,70)
                self.displayed_button_picto.y = picto_position[pos][1] + random.randint(-30,30)
            else :
                self.displayed_noise_picto[index].x = picto_position[pos][0] + random.randint(-70,70)
                self.displayed_noise_picto[index].y = picto_position[pos][1] + random.randint(-30,30)
            index = index + 1

    def verify_answer(self, buttons_pressed):
        if len(buttons_pressed) != 1:
            return False

        return buttons_to_sprites_hasmap[buttons_pressed[0]] == self.displayed_button_picto


class Score:
    def __init__(self):
        self.label = pyglet.text.Label('Score: 0000', font_size=100, font_name="Gobold_Light",
                                       x=(window.width*0.5), y=(window.height*0.9),
                                       anchor_x='center', anchor_y='center')
        self.reset()

    def reset(self):
        self.score = 0
        self.label.text = 'Score: 0000'
        self.label.color = (255, 255, 255, 255)

    def increment_score(self):
        self.score = self.score + config.POINTS_PER_ROUND
        self.label.text = 'Score: %04d' % (self.score)


class Timer:
    def __init__(self):
        self.pi = 3.14159
        self.label = pyglet.text.Label(str(config.ROUND_TIME), font_size=100, font_name="Gobold_Light",
                                       x=(window.width*0.9), y=(window.height*0.9),
                                       anchor_x='center', anchor_y='center')
                                       
        self.label.color = config.color_black                                       
        self.background_circle = pyglet.shapes.Circle( x=(window.width*0.9), y=(window.height*0.9), radius = 100, color = config.color_azur)
        self.front_circle = pyglet.shapes.Sector( x=(window.width*0.9), y=(window.height*0.9),
                                        radius = 101, color =config.color_lavande, start_angle = self.pi / 2, angle = 0)
        self.running = False
        self.reset_timer()

    def stop_timer(self):
        self.reset_timer()
        self.running = False

    def reset_timer(self):
        self.time = config.ROUND_TIME
        self.label.text = str(config.ROUND_TIME)


    def generate_front_circle(self):
        my_angle  = 2 * self.pi - (2 * self.pi * (10-self.time) / config.ROUND_TIME)
        self.front_circle = pyglet.shapes.Sector( x=(window.width*0.9), y=(window.height*0.9),
                                        radius = 101, color = config.color_lavande, start_angle = self.pi / 2, angle = my_angle)

    def update(self, dt):
        if self.running:
            self.time -= dt
            if (self.time <= 0):
                handle_loose()
            self.label.text = '%01d' % (round(self.time))




@window.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.ESCAPE:
        window.close()


@window.event
def on_draw():
    window.clear()

    background_sprite.draw()


    if game_state_running == True: 
        timer.background_circle.draw()
        timer.generate_front_circle()
        timer.front_circle.draw()
        timer.label.draw()

        score.label.draw()
        board.displayed_button_picto.draw()
        for sprites in board.displayed_noise_picto:
            sprites.draw()

    else: 
        waiting_label.draw()


buttons_to_sprites_hasmap = dict()
def build_hashmap():
    for i in range(len(path_buttons_picto)):
        index_img = int(os.path.basename(path_buttons_picto[i]).split('.')[0])
        buttons_to_sprites_hasmap[index_img] = sprite_buttons_picto[i]

##### Assets Imports

# Imports Images     

path_buttons_picto = [os.path.join(config.PATH_BUTTONS_PICTO, f) for f in os.listdir(config.PATH_BUTTONS_PICTO) if isCorrectPicto(os.path.join(config.PATH_BUTTONS_PICTO, f))]
path_noise_picto = [os.path.join(config.PATH_NOISE_PICTO, f) for f in os.listdir(config.PATH_NOISE_PICTO) if isCorrectPicto(os.path.join(config.PATH_NOISE_PICTO, f))]

img_buttons_picto = [pyglet.image.load(f) for f in path_buttons_picto]
img_noise_picto = [pyglet.image.load(f) for f in path_noise_picto]

sprite_buttons_picto = []
sprite_noise_picto = []

# Create sprites with correct size
resize_images()
build_hashmap()

background = pyglet.image.load( os.path.join(config.DIR_PATH, "./assets/images/background.png"))
background_sprite = pyglet.sprite.Sprite(background, x=0, y = 0)

# Font import
pyglet.font.add_file(os.path.join(config.DIR_PATH, "./assets/fonts/Gobold_Light.ttf"))
gobold_light = pyglet.font.load("Gobold_Light.ttf")

# Sounds import
if config.SOUND_MANAGEMENT:
    pyglet.options['audio'] = ('openal', 'pulse', 'directsound', 'silent')
    win_sound = pyglet.media.load(os.path.join(config.DIR_PATH, "./assets/sounds/validation_3.wav"))
    loose_sound = pyglet.media.load(os.path.join(config.DIR_PATH, "./assets/sounds/non_validation_3.wav"))

# Instantiate the game elements
timer = Timer()
score = Score()
board = Board()
waiting_label = pyglet.text.Label('MEMENTO', font_size=100, 
                                   x=window.width//2, y= window.height//2,
                                   anchor_x='center', anchor_y='center')


game_score = 0
if not config.USING_WS_SERVER:
    timer.running =  True
    game_state_running = True
else:
    timer.running =  False
    game_state_running = False


if __name__ == "__main__":

    config.convert_difficulty_to_nb_picto(board.difficulty)

    if config.USING_GPIO:
        gpio_management.gpio_init()
        pyglet.clock.schedule_interval(check_raspi_buttons, 1 / 30)

    if config.USING_WS_SERVER:
        pyglet.clock.schedule_interval(server_management.check_server_command, 1 / 30)
        pyglet.clock.schedule_interval(process_server_command, 1 / 30)


    pyglet.clock.schedule_interval(timer.update, 1/30.0)
    pyglet.app.run()




