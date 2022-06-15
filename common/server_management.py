import select
import json 
import sys
import os
import logging
import config

current_team_id = 0

def is_stdin_ready():
    read, _, _ = select.select([sys.stdin.fileno()], [], [], 0.0)
    return bool(read)


def check_server_command(_):
    global buffer
    if not is_stdin_ready():
        return
    data = os.read(sys.stdin.fileno(), 4096)
    if not data:
        logging.error("Websocat is not responding, leaving the game")
        sys.exit()

    buffer += data
    if b"\n" not in buffer:
        return

    index = buffer.rfind(b"\n") + 1
    commands = buffer[:index]
    buffer = buffer[index:]
    for command in commands.splitlines():
        parse_json_request(command.decode())


def handle_request_error(dct):
    logging.error("JSON Request is not formated properly")
    logging.error(dct)

def handle_stop_pc():
    logging.warning("Receive stop request, shutting the PC down")
    os.system("sudo shutdown -h now")

def parse_json_request(request):
    global current_team_id

    dct = dict()    
    try:
        dct = json.loads(request)
    except ValueError: 
        logging.error("Request is not properly formated in JSON")
        return
    
    # Expecting event/value keys in the request
    if ("event" not in dct) or ("value" not in dct):
        handle_request_error(dct)

    if dct["event"] == "stopAllPC":
            handle_stop_pc()
    elif dct["event"] == "roomStarted":
        # Request is not for me, drop it
        if int(dct["value"]["idRoom"]) != config.ROOM_ID:
            return

        logging.info("Received a game start event")
        # We record the team id 
        current_team_id = dct["value"]["idTeam"]

        if "language" in dct: 
            if dct["language"] == "fr":
                config.current_language = "fr"
            elif dct["language"] == "en":
                config.current_language = "en"
            else:
                logging.error(dct["language"] + " is not a supported language, set to default: fr")
                config.current_language = "fr"
        else:
            config.current_language = "fr"

        if "player" in dct: 
            if dct["player"] > 0 and dct["player"] < 4: 
                config.current_nb_players = dct["player"]
            else: 
                config.current_nb_players = 4

        #print("Received a game start event")
        config.process_server_start = True

    elif dct["event"] == "roomStopped":

        if int(dct["value"]) != config.ROOM_ID:
            return

        logging.info("Received a game stop event")
        config.process_server_stop = True

    elif dct["event"] == "stopPC":

        if int(dct["value"]) != config.ROOM_ID:
            return
        handle_stop_pc()
    else:
        handle_request_error(dct)


def send_request_score(score):
    global current_team_id
    request = dict()
    request["event"] = "setScore"
    request["value"] = { "idRoom" : config.ROOM_ID, "score" : score, "idTeam" : current_team_id}

    print(json.dumps(request))
