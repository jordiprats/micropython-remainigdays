#!/bin/bash

pkill screen

for file in main.py config.py ../micropython-utelegram/utelegram.py;
do
    echo "refreshing $file"
    ampy --port /dev/ttyUSB0 rm $file
    ampy --port /dev/ttyUSB0 put $file
done