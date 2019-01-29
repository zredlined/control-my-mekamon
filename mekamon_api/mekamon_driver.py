#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Python app and flask API to enable control of
a Mekamon v1 or v2 robot.
https://mekamon.com
"""

__author__      = "Alex Watson"
__copyright__   = "Copyright 2018"
 
import logging
import numpy as np
import sys
import time

import Adafruit_BluefruitLE
from Adafruit_BluefruitLE.services import UART, DeviceInformation

from utils import generate_cmd, unhexlify

def main():

    # Set up logging
    logging_format = '%(asctime)s : %(processName)s : %(levelname)s : %(message)s'
    logging_level = logging.INFO
    logging.basicConfig(format=logging_format, level=logging_level)
    logging.info("running %s", " ".join(sys.argv))
 
    # Clear any cached data because both bluez and CoreBluetooth have issues with
    # caching data and it going stale.
    ble.clear_cached_data()
 
    # Get the first available BLE network adapter and make sure it's powered on.
    adapter = ble.get_default_adapter()
    adapter.power_on()
    logging.info('Using adapter: {0}'.format(adapter.name))
 
    # Disconnect any currently connected UART devices.  Good for cleaning up and
    # starting from a fresh state.
    logging.info('Disconnecting any connected UART devices...')
    UART.disconnect_devices()
 
    # Scan for UART devices.
    logging.info('Searching for UART devices...')
    adapter.start_scan()

    mekamon_device = None
    time_end = time.time() + 10 # search for x secs

    while time.time() < time_end and mekamon_device is None:
        # Call UART.find_devices to get a list of any UART devices that
        # have been found.  This call will quickly return results and does
        # not wait for devices to appear.
        found = set(UART.find_devices())
        # Check for new devices that haven't been seen yet and logging.info out
        # their name and ID (MAC address on Linux, GUID on OSX).
        for device in found:
            if 'Meka' in device.name:
                logging.info('  -- Found Mekamon: {0} [{1}]'.format(device.name, device.id))
                mekamon_device = device

        # Sleep for a second and see if new devices have appeared.
        if mekamon_device is None:
            time.sleep(1.00)
 
    # Make sure scanning is stopped before exiting.
    logging.info("  -- Stopping scan...")
    adapter.stop_scan()
 
    logging.info('Connecting to Mekamon: {0} [{1}]'.format(mekamon_device.name, mekamon_device.id))
    mekamon_device.connect(timeout_sec=10)  

    logging.info('  -- Discovering BLE services')
    UART.discover(mekamon_device)

    # Once service discovery is complete create an instance of the service
    # and start interacting with it.
    mekamon_uart = UART(mekamon_device)
 
    # list of initial MM messages.
    init1 = [16] # 02101300
    init2 = [7,1] # 0307010c00
    motion_neutral = [6,0,0,0] # 02060101010c00
 
    msgList = np.array([init1, init2, motion_neutral])
 
    for index, msg in enumerate(msgList):
        msgOut = generate_cmd(msg)
        logging.info("  -- Pwning Mekamon message %d/%d: %s", index, len(msgList), msgOut)   
 
        #msgOut = str.encode(msgOut) # convert to bytes
        msgOut = unhexlify(msgOut)
        mekamon_uart.write(msgOut)
 
        time.sleep(0.5)

    # Setup complete. main program loop here
    x = 0
    try: 
        logging.info("Sending motion commands")
        while x < 2:
            # convert velocities to MM values ([-80...80])
     
            limit = 80 # max +/- 127
     
            time.sleep(0.2) 
     
            strafe = 0
            fwd = 0
            turn = 10

            x = x+1

            msgOut = generate_cmd([6, strafe, fwd, turn]) # 6=motion
            logging.info('strafe: %d fwd: %d turn: %d [%s]' % (strafe, fwd, turn, msgOut))
     
            #msgOut = str.encode(msgOut)
            msgOut = unhexlify(msgOut)
            mekamon_uart.write(msgOut)
            time.sleep(1)

        msgOut = generate_cmd([6, 0, 0, 0]) # 6=motion
        logging.info('Stopping all motion [%s]' % (msgOut))
        msgOut = unhexlify(msgOut)
        mekamon_uart.write(msgOut)

    finally:
        logging.info("Disconnecting BLE from Mekamon")
        mekamon_device.disconnect()

 
# Get the BLE provider for the current platform.
ble = Adafruit_BluefruitLE.get_provider()
 
# Initialize the BLE system.  MUST be called before other BLE calls!
ble.initialize()
 
# Start the mainloop to process BLE events, and run the provided function in
# a background thread.  When the provided main function stops running, returns
# an integer status code, or throws an error the program will exit.
ble.run_mainloop_with(main)
 
