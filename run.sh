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
echo "#                                                        #"
echo "#           DEV VERSION 3.1   Linux startup              #"
echo "#                                                        #"
echo "##########################################################"

# python3 app/scripts/main.py -launch_bot --name=Test --debug_mode=True --advanced_logging=True
# python3 app/scripts/main.py -add_serv --serv_data='{"me":{"host": "localhost", "port": 25575, "password": "sosalubomjaovoch"}}'
python3 app/scripts/main.py -show_serv -show_db -launch_bot --name=Test --debug_mode=True --advanced_logging=True
#python3 app/scripts/main.py -test


read -p "Press any key..."
