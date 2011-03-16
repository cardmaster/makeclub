#!/bin/bash
SCRIPT_FOLDER=`dirname $0`
APP_FOLDER=`readlink -f $SCRIPT_FOLDER/../`
LOG_FOLDER=$APP_FOLDER/log
DEV_SERVER=dev_appserver.py
echo Application = $APP_FOLDER
if [ ! -d $LOG_FOLDER ]; then
	mkdir -p $LOG_FOLDER
fi
LOG_FILE=`date +%F.%H-%M-%S`.log
echo Write log to file $LOG_FILE
$DEV_SERVER $@ $APP_FOLDER # 2>&1 >$LOG_FOLDER/$LOG_FILE 
echo Run server as PID $!
