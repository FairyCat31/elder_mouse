env/Scripts/activate.ps1
$env:PYTHONPATH = $PWD.Path
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
echo "#           DEV VERSION 3.1   Windows startup            #"
echo "#                                                        #"
echo "##########################################################"

# python3 app/scripts/main.py -launch_bot --name=Test --debug_mode=True --advanced_logging=True
#python app/scripts/main.py -show_db -add_db --db_data="{'test':{'DB_NAME': 'pyth_database', 'DB_HOST':'89.46.131.209', 'DB_PORT':3306, 'DB_USER':'pyth', 'DB_PASS':'7vd6aOgn2808POd@QVoZmIXYzpSjrO~9@~RC@P4kIYgO5w6p0YJzuL}wNw8n}3ObEyWRnIrj'}}" -show_db
#python app/scripts/main.py -launch_bot --name="Elder Mouse" --debug_mode=True --advanced_logging=True
python app/scripts/main.py -launch_bot --name=Test --debug_mode=True --advanced_logging=True
#python app/scripts/main.py -test
pause