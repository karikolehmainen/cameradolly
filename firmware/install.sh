#!/bin/sh

apt-get -y install gphoto2
apt-get -y install libgphoto2-dev
apt-get -y install mosquitto
apt-get -y install mosquitto-clients
apt-get -y install python3-pip
apt-get -y install python3-setuptools
apt-get -y install python3-dev

pip3 install wheel
pip3 install gphoto2
pip3 install paho-mqtt
pip3 install Adafruit_LSM303
pip3 install Adafruit_ADS1x15
pip3 install Adafruit_MotorHAT
pip3 install pytz

cp cameradolly.json /etc/
cp cameradolly.service /etc/systemd/system/
systemctl daemon-reload
systemctl start mosquitto
systemctl start cameradolly
