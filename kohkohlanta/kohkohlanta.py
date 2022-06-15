#!/usr/bin/env python

import os
import sys
import pyglet
import random
import logging
import time
import config

if config.USING_WS_SERVER:
    sys.path.insert(0,os.path.realpath(os.path.join(config.DIR_PATH,"../common")))
    import server_management

import gpio_management


window = pyglet.window.Window(fullscreen=True)

def process_server_command(_):

    global game_score, game_state_running
    
    if config.process_server_stop:
        if not game_state_running:
            logging.warning("Attempting to stop a game already stopped ??")
        server_management.send_request_score(score.score)
        game_state_running = False
        config.process_server_stop = False
        game.process_stop()

    if config.process_server_start:
        if game_state_running:
            logging.warning("Attempting to start a game already started")

        game_state_running = True
        config.process_server_start = False
        ok_time = 0
        score.reset()

class Game:
    def __init__(self):
        self.reset_game()
    def set_music(self, is_win = True):
        if not config.SOUND_MANAGEMENT:
            return 

        if player1.playing:
            player1.pause()
            player1.next_source()
        if player2.playing:
            player2.pause()
            player2.next_source()
        
        if is_win:
            player1.queue(ready_sound)
            player2.queue(epic_rap_choir)
            player2.loop = True
        else:
            player1.queue(floor_detect_sound)
        
        player1.play()
        player2.play()

    def process_stop():
        self.reset_disturbances()
        self.reset_game()

        if config.SOUND_MANAGEMENT:
            stop_music()
            player1.queue(floor_detect_sound)
            player1.play()
    
    
    def reset_game(self):
        self.ok_time = 0
        self.reset_state()

    def reset_state(self):
        self.score_running = False
        self.current_ok_time = 0
        self.last_scored_time = 0
        self.start_fan = False
        self.start_light = False
        self.start_strobo = False

    def get_status_text(self):
        nb_poles_activated = gpio_management.nb_people_detected()
        if gpio_management.is_floor_activated() or  nb_poles_activated != config.current_nb_players:
            return "Montez sur les poteaux"
        else: 
            return "Gardez la position"

    def pop_warning(self):
        display_warning = True


    def check_players_state(self, dt):

        if not game_state_running:
            reason_label.text = ""
            return

        if gpio_management.nb_people_detected() == config.current_nb_players and not gpio_management.is_floor_activated():
            if self.score_running == False:
                self.score_running = True
                self.current_ok_time = 0
                self.last_scored_time = 0
                self.set_music(is_win = True)
            else:
                #Score running , programming disturbances
                self.ok_time = self.ok_time + dt
                self.current_ok_time = self.current_ok_time + dt

                # Managing FAN
                if "FAN" in self.current_disturbance() and self.start_fan == False:
                    self.activate_fan()
                elif "FAN" not in self.current_disturbance() and self.start_fan == True:
                    self.deactivate_fan()

                # Managing Light
                if "LIGHT" in self.current_disturbance() and self.start_light == True:
                    self.deactivate_light()
                elif "LIGHT" not in self.current_disturbance() and self.start_light == False:
                    self.activate_light()

                # Managing Stroboscope
                if "STROBO" in self.current_disturbance() and self.start_strobo == False:
                    self.activate_strobo()
                elif "STROBO" not in self.current_disturbance() and self.start_strobo == True:
                    self.deactivate_strobo()

                # Managing score increment
                if (self.current_ok_time - self.last_scored_time) >= 1:
                    score.increment_score()
                    self.last_scored_time = self.current_ok_time

                reason_label.text = ""

        else:
            if self.score_running == True:
                self.reset_state()
                self.reset_disturbances()
                self.set_music(is_win = False)
                self.pop_warning()

            else:
                # Managing the score decrement
                self.current_ok_time = self.current_ok_time + dt
                if (self.current_ok_time - self.last_scored_time) >= 1:
                    score.decrement_score()
                    self.last_scored_time = self.current_ok_time

    def people_detection(self):
        global ground_detection
        if not config.USING_GPIO:
            if ground_detection:
                return 0
            else:
                return 2
        else:
            if len(gpio_management.check_button_press()) > 0:
                return 0
            else:
                return 2

    def activate_light(self):
        #print("activate_light")
        if not start_light:
            self.start_light = True
            gpio_management.activate_relay()

    def deactivate_light(self):
        #print("desactivate_light")
        if start_light:
            self.start_light = False
            gpio_management.deactivate_relay()

    def activate_fan(self):
        #print("activate_fan")
        if not self.start_fan:
            self.start_fan = True
            gpio_management.activate_fan()

    def deactivate_fan(self):
        #print("desactivate_fan")
        if self.start_fan: 
            self.start_fan = False
            gpio_management.deactivate_fan()


    def activate_strobo(self):
        #print("activate_stro")
        if not self.start_strobo:
            self.start_strobo = True
            gpio_management.activate_strombo()

    def deactivate_strobo(self):
        #print("desactivate_strobo")
        if self.start_strobo:
            self.start_strobo = False
            gpio_management.deactivate_strombo()
    
    def reset_disturbances(self):
        self.deactivate_strobo()
        self.deactivate_fan()
        self.activate_light()


    def current_disturbance(self):
        result = []
        if self.ok_time >= config.FAN_TRIGGER and self.ok_time < (config.FAN_TRIGGER + config.FAN_DURATION):
            result.append("FAN")
        if self.ok_time >= config.STROBO_TRIGGER and self.ok_time < (config.STROBO_TRIGGER + config.STROBO_DURATION):
            result.append("STROBO")
        if self.ok_time >= config.LIGHT_TRIGGER and self.ok_time < (config.LIGHT_TRIGGER + config.LIGHT_DURATION):
            result.append("LIGHT")
        return result


class Score:
    def __init__(self):
        self.label = pyglet.text.Label('Score: 0000', font_size=80, font_name="Gobold Thin Light",
                                       x=window.width//2, y=window.height*0.80, color = (255,255,255,255),
                                       anchor_x='center', anchor_y='center')
        self.reset()

    def increment_score(self):
        self.score = self.score + config.INCREMENT_SCORE_PER_SEC
        self.label.text = 'Score: %04d' % (self.score)

    def decrement_score(self):
        self.score = self.score + config.DECREMENT_SCORE_PER_SEC
        self.label.text = 'Score: %04d' % (self.score)

    def reset(self):
        self.score = 0
        self.label.text = 'Score: 0000'


def stop_music():
    player1.pause()
    player1.next_source()
    player2.pause()
    player2.next_source()

@window.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.ESCAPE:
        if config.SOUND_MANAGEMENT:
            stop_music()
        window.close()



@window.event
def on_draw():
    window.clear()
    background_sprite.blit(0,0)
    reason_label.text = game.get_status_text()
    
    if game_state_running == True:
        score.label.draw()
        if game.score_running:
            ok_sprite.draw()
        else:
            error_sprite.draw()
        
        reason_label.draw()
    else:
        waiting_label.draw()


# Font import
pyglet.font.add_file(os.path.join(config.DIR_PATH, "./assets/fonts/Gobold_Light.ttf"))
gobold_light = pyglet.font.load("Gobold Thin Light")

# Sounds import
if config.SOUND_MANAGEMENT:
    pyglet.options['audio'] = ('openal', 'pulse', 'directsound', 'silent')
    ready_sound = pyglet.media.load(os.path.join(config.DIR_PATH, "./assets/sounds/are_you_ready.mp3"))
    floor_detect_sound = pyglet.media.load(os.path.join(config.DIR_PATH, "./assets/sounds/non_validation_3.wav"))
    epic_rap_choir = pyglet.media.load(os.path.join(config.DIR_PATH, "./assets/sounds/epic_rap_choir.wav"))


player1 = pyglet.media.Player()
player2 = pyglet.media.Player()
# Instantiate the game elements
score = Score()
game = Game()

reason_label = pyglet.text.Label('', font_size=80, font_name="Gobold Thin Light",
                                   x=window.width//2, y= window.height*0.6,
                                   anchor_x='center', anchor_y='center')


waiting_label = pyglet.text.Label('Koh Koh Lanta', font_size=50, font_name="Gobold Thin Light",
                                   x=window.width//2, y= window.height//2,
                                   anchor_x='center', anchor_y='center')


background_sprite = pyglet.image.load(os.path.join(config.DIR_PATH, "./assets/images/background.png"))

width = 200

error_img = pyglet.image.load(os.path.join(config.DIR_PATH, "./assets/images/error.png"))
error_img.anchor_x = error_img.width // 2
error_img.anchor_y = error_img.height // 2
error_sprite = pyglet.sprite.Sprite(error_img, x=window.width//2, y = window.height*0.3)
error_sprite.scale = width / window.width

ok_img = pyglet.image.load(os.path.join(config.DIR_PATH, "./assets/images/ok.png"))
ok_img.anchor_x = ok_img.width // 2
ok_img.anchor_y = ok_img.height // 2
ok_sprite = pyglet.sprite.Sprite(ok_img, x=window.width//2, y = window.height*0.3)
ok_sprite.scale = width / window.width

if config.USING_WS_SERVER:
    game_state_running = False
else :
    # If we do not use the websocket server, the game is launched automatically
    game_state_running = True

if __name__ == "__main__":
    if config.USING_GPIO:
        gpio_management.gpio_init()

    if config.USING_WS_SERVER:
        pyglet.clock.schedule_interval(server_management.check_server_command, 1 / 30)
        pyglet.clock.schedule_interval(process_server_command, 1 / 30)

    pyglet.clock.schedule_interval(game.check_players_state, 1/30.0)

    pyglet.app.run()




