#!/bin/bash 

set -o pipefail

DEFAULT_PORT=12345
DEFAULT_SERVER="ws://192.168.1.9"

usage() {

  echo "This script launches the 1055/Koh Koh Lanta game"
  echo "This script tries to connect every second to the websocket server, then launch the game"
  echo "If the game crashes or gets disconnected, the game restarts" 
  echo "By default, the websocket server address used is ${DEFAULT_SERVER}:${DEFAULT_PORT}"
  echo "Usage: launch_forever.sh [--port PORT --server SERVER] -g/--game GAME"
  echo "GAME parameter can be memento, kohkohlanta, quizzextreme"
}

PORT=${DEFAULT_PORT}
SERVER=${DEFAULT_SERVER}
GAME=""

while [[ $# -gt 0 ]]; do
  case $1 in
    -p|--port)
      PORT="$2"
      shift # past argument
      shift # past value
      ;;
    -s|--server)
      SERVER="$2"
      shift # past argument
      shift # past value
      ;;
    -g|--game)
      GAME="$2"
      shift # past argument
      shift # past value
      ;;
    -*|--*)
      echo "Unknown option $1"
      usag
      exit 1
      ;;
    *)
      POSITIONAL_ARGS+=("$1") # save positional arg
      usage
      shift # past argument
      ;;
  esac 
done

if [ -z $GAME ];then
  echo "No game parameter specified"
  usage
  exit 1
fi


CURRENT_DIR=$( dirname -- "${BASH_SOURCE[0]}" )
cd $CURRENT_DIR


fifo_name=fifo_${GAME}
rm ${fifo_name}
mkfifo ${fifo_name}


while :
do
  echo "Connecting to the websocket server $SERVER:$PORT ..."
  cat ${fifo_name} | websocat -E $SERVER:$PORT | python3 ./${GAME}/${GAME}.py > ${fifo_name}
  echo "${GAME} game has been stopped, attempt to relaunching it"
  sleep 1
done



