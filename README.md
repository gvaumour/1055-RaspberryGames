# Raspberry Games 


## Memento

Variation of the doodle game, you have to find the only symbol on the picture that is printed on one of the push button in front of you

## Koh Koh Lanta

A game where people are meant to stay on poles with several disturbance to make them fall
There is a detection mecanism for the poles and for the ground 

## Quizz de l'extreme 

Displays a MCQ on the screen, the players has to push buttons from A to D to answer
It interacts with a centralized server that sends json requests through websockets that start and stop the game




# Installation 

All games have the sames dependencies to be install 

*Game engine:*
The script runs with python3-8-10, the game engine use the pyglet package v1.5.21

````
apt-get install python3 python3-dev i2c-tools ffmpeg python3-gst-1.0 libglu1-mesa
pip3 install pyglet RPi.GPIO smbus
````

*Web socket Management:*
The websocket service is managed with the [websocat][2] project: 

It receives data from a web socket and print it in stdout as text
You need to download the builtin version for your specific platform.
For raspberry, the linuxarm32 pre-build is available [here][1], v1.9.0 is used for the project


# Run 

The script **launch_forever.sh** will run the game. If for any reasons,
the game is left, for example, if the websocket connection is broken, 
it will continously try to restart the game


# Changelog

* First release v1: 28/01/2022


Author: Gregory Vamourin 

[1]: https://github.com/vi/websocat/releases/download/v1.9.0/websocat_linuxarm32
[2]: https://github.com/vi/websocat/releases
