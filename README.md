# control-my-mekamon

This is an API to enable programmatic control and unlock the possibilities for what you can do with the fantastic Mekamon robot (https://mekamon.com). 

## What you'll need:
* Mekamon beserker robot - available from the Apple store
* Raspberry Pi, running Raspbian or Debian
* A Bluetooth Low Energy controller (USB) based on the CSR8510 chip ($6.99 on Amazon)
* Python 2.7 or 3.5 supported

## Bluetooth setup
Linux, using the latest BlueZ 5.33 release. The library is implemented using BlueZ's experimental DBus bindings for access from languages such as Python.

Follow the instructions at https://github.com/adafruit/Adafruit_Python_BluefruitLE/ to get Bluetooth set up on your Raspberry Pi to send messages from your Pi to the Mekamon.

## Running the API

Install necessary Python packages
```bash
pip install -e requirements.txt
```

First, start the server
```bash
python -m mekamon_api.mekamon_driver
```

Next, start the Pygame client to control your Mekamon with the keyboard ('w','a','s','d' keys for directions)
```bash
python -m mekamon_control.keyboard_controller
```


