#!/usr/bin/env python

import os

import sys
import pyglet
import random
import logging

import config 

if config.USING_WS_SERVER:
    sys.path.insert(0 , os.path.realpath(os.path.join(config.DIR_PATH , "../common")))
    import server_management

import gpio_management


window = pyglet.window.Window(fullscreen=True)

questions_fr_list = []
questions_en_list = []
questions_list = []

answer_position = [ [window.width*0.05, window.height*0.32],
                    [window.width*0.50, window.height*0.32],
                    [window.width*0.05, window.height*0.02],
                    [window.width*0.50, window.height*0.02]
                 ]

button_to_answer_array = {0 : 'A', 1:'B', 2 : 'C', 3 : 'D'}

def parse_questions_file(file):
    result =[]
    with open(os.path.join(config.DIR_PATH, file), encoding='utf8') as f:
        lines = f.readlines()

    for line in lines:

        if line == "":
            continue

        split_line = line.strip().split(':')
        entete = split_line[0].lower()
        if entete == "question":
            entry = [ ':'.join(split_line[1::]) ]
        elif entete == "bonne reponse":
            bonne_reponse = split_line[1].strip()
            entry.append(bonne_reponse)
            result.append(entry)
        elif entete == "a" or entete == "b" or entete == "c" or entete == "d":
            entry.append(':'.join(split_line[1::]))
    return result

def check_raspi_gpio(_):

    if not game_state_running:
        return

        ground_state = gpio_management.is_ground_detection_activated()
        board.check_ground_activation(ground_state)

        # Check if the lidar detection is activated
        board.lidar_activated = gpio_management.is_lidar_activated()

    else:
        board.check_ground_activation(tmp_ground_detection)



class Timer:
    def __init__(self):
        self.pi = 3.14159
        self.label = pyglet.text.Label(str(config.WAIT_TIME), font_size=300, font_name="Gobold_Light",
                                       x=(window.width*0.5), y=(window.height*0.5),
                                       anchor_x='center', anchor_y='center')
                                       
        self.label.color = config.color_black                                       
        self.background_circle = pyglet.shapes.Circle( x=(window.width*0.5), y=(window.height*0.5), radius = 300, color = config.color_azur)
        self.front_circle = pyglet.shapes.Sector( x=(window.width*0.5), y=(window.height*0.5),
                                        radius = 302, color =config.color_lavande, start_angle = self.pi / 2, angle = 0)
        self.running = False
        self.reset_timer()

    def stop_timer(self):
        self.reset_timer()
        self.running = False

    def reset_timer(self):
        self.time = config.WAIT_TIME
        self.label.text = str(config.WAIT_TIME)

    def start(self):
        self.reset_timer()
        self.running = True

    def generate_front_circle(self):
        my_angle  = 2 * self.pi - (2 * self.pi * (10-self.time) / config.WAIT_TIME)
        self.front_circle = pyglet.shapes.Sector( x=(window.width*0.5), y=(window.height*0.5),
                                        radius = 302, color = config.color_lavande, start_angle = self.pi / 2, angle = my_angle)

    def update(self, dt):
        if self.running:
            self.time -= dt
            if (self.time <= 0):
                board.finished_timer()
            self.label.text = '%01d' % (round(self.time))





def process_server_command(_):

    global game_score, game_state_running, questions_list
    
    if config.process_server_stop:
        if not game_state_running: 
            logging.warning("Attempting to stop a game already stopped ??")
        server_management.send_request_score(score.score)
        game_state_running = False
        config.process_server_stop = False
        board.process_stop()
    
    if config.process_server_start:
        if game_state_running: 
            logging.warning("Attempting to start a game already started")

        if config.current_language == "en":
            questions_list = questions_en_list
        else:
            questions_list = questions_fr_list
        board.flush_questions_history()

        game_state_running = True
        config.process_server_start = False
        score.reset()
        board.do_next_round()



class Board:
    def __init__(self):

        self.batch = pyglet.graphics.Batch()

        self.question = pyglet.text.document.FormattedDocument("Question")
        self.question.set_style(0, len(self.question.text), dict(font_name ='Gobold Thin Light', font_size = 60, color =(255, 255, 255, 255), align = 'center'))
        self.question.x = window.width//2
        self.question.y = window.height
        self.question.anchor_x ='center'
        self.question.anchor_y='center'
        self.question_layout = pyglet.text.layout.TextLayout(self.question, width = window.width*0.9, height = window.height*0.8, batch = self.batch, multiline = True, wrap_lines = True)
        self.question_layout.x = window.width*0.05

        self.answers = [None]*4
        self.answers_layout = [None]*4
        self.answers_rect = []
        self.win_sound_player = pyglet.media.Player()
        self.loose_sound_player = pyglet.media.Player()
        self.reset_game()


        for i in range(4):
            self.answers[i] = pyglet.text.document.FormattedDocument("Reponse")
            self.answers[i].set_style(0, len(self.answers[i].text), dict(font_name ='Gobold Thin Light', font_size = 50, color =(2,2,2,255), align = 'center'))

            self.answers_layout[i] = pyglet.text.layout.TextLayout(self.answers[i], width = window.width*0.35, height = config.HEIGHT_REPONSE, 
                                   batch = self.batch, multiline = True, wrap_lines = True)

            self.answers_layout[i].x = answer_position[i][0] + 100
            self.answers_layout[i].y = answer_position[i][1] - 30

            # White rectangle that contains the answer
            self.answers_rect.append(pyglet.sprite.Sprite(frame_answer, x = answer_position[i][0], y = answer_position[i][1]))
            self.label = pyglet.text.Label(button_to_answer_array[i], font_size=50, font_name="Gobold Thin Light",
                                      x=answer_position[i][0]+60, y=answer_position[i][1]+120, 
                                      anchor_x='center', anchor_y='center', batch = self.batch)

        self.do_next_round()

    def process_stop(self):
    
        if config.SOUND_MANAGEMENT:
            self.win_sound_player.pause()
            self.loose_sound_player.next_source()

        reset_game()

    def reset_game(self):
        self.ground_detection_activated = False
        self.lidar_activated = False
        self.timer_is_run = False
        self.old_questions = []


    def check_answer(self, buttons_pressed):
        if len(buttons_pressed) == 1 and button_to_answer_array[buttons_pressed[0]] == self.good_answer:
            score.increment_score()
            if config.SOUND_MANAGEMENT:
                if self.win_sound_player.playing:
                    self.win_sound_player.pause()
                    self.win_sound_player.next_source()
                self.win_sound_player = win_sound.play()
        else:
            score.decrement_score()
            if config.SOUND_MANAGEMENT:
                if self.loose_sound_player.playing:
                    self.loose_sound_player.pause()
                    self.loose_sound_player.next_source()
                self.loose_sound_player = wrong_answer_sound.play()
                
        self.do_next_round()

    def finished_timer(self):
        self.timer_is_run = False
        timer.reset_timer()
        self.do_next_round()

    def check_ground_activation(self, ground_activated):
        if not self.ground_detection_activated and ground_activated:
            # The ground detection has just been activated, we play a sound
            if config.SOUND_MANAGEMENT:
                ground_detection_sound.play()

        if self.ground_detection_activated and not ground_activated:
            # The ground detection is deactivated , launching the timer
            self.timer_is_run = True
            timer.start()

        self.ground_detection_activated = ground_activated

    def flush_questions_history(self):
        self.old_questions = []

    def do_next_round(self):

        # Pick a random question, we are just keep track of questions asked this session so we do not repeat
        index_question = random.randrange(len(questions_list))
        while index_question in self.old_questions:
            index_question = random.randrange(len(questions_list))

        self.old_questions.append(index_question)
        if len(questions_list) == len(self.old_questions):
            logging.error("I am out of new questions for this game, flush questions history")
            self.old_questions = []

        # Update labels texts
        self.question.text = questions_list[index_question][0]
        self.answers[0].text = questions_list[index_question][1]
        self.answers[1].text = questions_list[index_question][2]
        self.answers[2].text = questions_list[index_question][3]
        self.answers[3].text = questions_list[index_question][4]
        self.good_answer = questions_list[index_question][5]


class Score:
    def __init__(self):
        self.label = pyglet.text.Label('Score: 0000', font_size=100, font_name="Gobold Thin Light",
                                       x=(window.width//2), y=(window.height - window.height*0.08),
                                       anchor_x='center', anchor_y='center')
        self.reset()

    def increment_score(self):
        self.score = self.score + config.INCREMENT_SCORE
        self.label.text = 'Score: %04d' % (self.score)

    def decrement_score(self):
        self.score = self.score + config.DECREMENT_SCORE
        self.label.text = 'Score: %04d' % (self.score)

    def reset(self):
        self.score = 0
        self.label.text = 'Score: 0000'
        self.label.color = (255, 255, 255, 255)



tmp_ground_detection = False

@window.event
def on_key_press(symbol, modifiers):
    global tmp_ground_detection
    if symbol == pyglet.window.key.ESCAPE:
        window.close()
    if symbol == pyglet.window.key.SPACE:
        board.check_answer([])

    # We emulate the GPIO from keyboard for testing purposes
    if not config.USING_GPIO:
        if symbol == pyglet.window.key.ENTER:
            tmp_ground_detection = not tmp_ground_detection 



def get_reason_text():
    if not board.lidar_activated:
        return "Placez vous sous le projecteur pour avoir la question"
    elif board.ground_detection_activated:         
        return "Ne touchez pas la surface des tatamis"
    else:
        return " "

@window.event
def on_draw():
    window.clear()

    background_sprite.draw()


    if game_state_running == True: 

        # Ethier ground detection is activated
        if board.ground_detection_activated or not board.lidar_activated:
            reason_label.text = get_reason_text()

            error_sprite.draw()
            reason_label.draw()
    
        # Ether we tempo a few seconds between ground detection and the game
        #elif board.timer_is_run:
        #    timer.background_circle.draw()
        #    timer.generate_front_circle()
        #    timer.front_circle.draw()
        #    timer.label.draw()
        # Just printing the questions
        else: 
            score.label.draw()
            for rect in board.answers_rect:
                rect.draw()
            board.batch.draw()

    else: 
        waiting_label.draw()

##### Assets Imports
background_sprite = pyglet.shapes.Rectangle(x = 0, y = 0, width = window.width, height = window.height, color = (2,2,2)) 

reason_label = pyglet.text.Label('', font_size=60, font_name="Gobold Thin Light",
                                   x=window.width//2, y= window.height*0.75,
                                   anchor_x='center', anchor_y='center')


frame_answer = pyglet.image.load( os.path.join(config.DIR_PATH, "./assets/images/frame.png"))
frame_answer.anchor_x = 0 #frame_answer.width // 2
frame_answer.anchor_y = 0 #frame_answer.height // 2

width = 200
error_img = pyglet.image.load(os.path.join(config.DIR_PATH, "./assets/images/error.png"))
error_img.anchor_x = error_img.width // 2
error_img.anchor_y = error_img.height // 2
error_sprite = pyglet.sprite.Sprite(error_img, x=window.width//2, y = window.height*0.3)
error_sprite.scale = width / window.width


# Font import
pyglet.font.add_file(os.path.join(config.DIR_PATH, "./assets/fonts/Gobold_Light.ttf"))
gobold_light = pyglet.font.load("Gobold Thin Light")

# Sounds import
if config.SOUND_MANAGEMENT:
    pyglet.options['audio'] = ('openal', 'pulse', 'directsound', 'silent')
    win_sound = pyglet.media.load(os.path.join(config.DIR_PATH, "./assets/sounds/validation_4.wav"))
    wrong_answer_sound = pyglet.media.load(os.path.join(config.DIR_PATH, "./assets/sounds/non_validation_3.wav"))
    ground_detection_sound = pyglet.media.load(os.path.join(config.DIR_PATH, "./assets/sounds/non_validation_4.wav"))

# Populate questions 
questions_fr_list = parse_questions_file(config.QUESTIONS_FILE_FR)
questions_en_list = parse_questions_file(config.QUESTIONS_FILE_EN)

if config.current_language == "en":
    questions_list = questions_en_list
else:
    questions_list = questions_fr_list


# Instantiate the game elements
score = Score()
timer = Timer()
board = Board()
waiting_label = pyglet.text.Label('Quizz de l\'extrême', font_size=100, 
                                   x=window.width//2, y= window.height//2,
                                   anchor_x='center', anchor_y='center')



if not config.USING_WS_SERVER:
    # If we do not use the websocket server, the game is launched automatically
    game_state_running = True
else :
    game_state_running = False

if __name__ == "__main__":
    if config.USING_WS_SERVER:
        pyglet.clock.schedule_interval(server_management.check_server_command, 1 / 30)
        pyglet.clock.schedule_interval(process_server_command, 1 / 30)

    if config.USING_GPIO:
        gpio_management.gpio_init()
    pyglet.clock.schedule_interval(check_raspi_gpio, 1 / 30)
    pyglet.clock.schedule_interval(timer.update, 1/30.0)

    pyglet.app.run()




