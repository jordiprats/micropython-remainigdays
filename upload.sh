#!/bin/bash

if [ -z "$1" ] || [ -z "$2" ];
then
    echo $0 <SSID> <PASSW0RD>
fi

cat main_template.py | sed "s/_SSID_/$1/" | sed "s/_PASSWORD_/$2/" > main.py
pkill screen
ampy --port /dev/ttyUSB0 rm main.py
ampy --port /dev/ttyUSB0 put main.py

