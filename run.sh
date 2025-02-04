#!/bin/bash

source env/bin/activate
export PYTHONPATH=$(pwd)
echo "##########################################################"
echo "#                                                        #"
echo "#    ______       ______         _                       #"
echo "#    | ___ \      |  ___|       | |                      #"
echo "#    | |_/ /   _  | |_ __ _  ___| |_ ___  _ __ _   _     #"
echo "#    |  __/ | | | |  _/ _  |/ __| __/ _ \| '__| | | |    #"
echo "#    | |  | |_| | | || (_| | (__| || (_) | |  | |_| |    #"
echo "#    \_|   \__, | \_| \__,_|\___|\__\___/|_|   \__, |    #"
echo "#           __/ |                               __/ |    #"
echo "#          |___/                               |___/     #"
echo "#                                                        #"
echo "##########################################################"
echo "\n"
echo "DEV VERSION 3.1"
python3 app/scripts/main.py -launch_bot --name=Test --debug_mode=True --advanced_logging=True

read -p "Press any key..."
