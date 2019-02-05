#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Python app and flask API to enable control of
a Mekamon v1 or v2 robot.
https://mekamon.com
"""

__author__      = "Alex Watson"
__copyright__   = "Copyright 2019"
 
import logging
import numpy as np
import socket
import sys
import time

import Adafruit_BluefruitLE
from Adafruit_BluefruitLE.services import UART, DeviceInformation

import config
from motion_controller import MotionController
from utils import execute_cmds, execute_cmd

def main():

    # Set up logging
    logging_format = '%(asctime)s : %(filename)s : %(levelname)s : %(message)s'
    logging_level = logging.INFO
    logging.basicConfig(format=logging_format, level=logging_level)
    logging.info("Running %s", " ".join(sys.argv))

    # Declare our serverSocket upon which
    # we will be listening for UDP messages
    logging.info('Initializing Mekamon UDP listener on %s:%s' % (config.UDP_IP_ADDRESS,
        config.UDP_PORT_NO))
    serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serverSock.bind((config.UDP_IP_ADDRESS, config.UDP_PORT_NO))

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
 
    # Set up motion controller and initialize Mekamon
    motion_controller = MotionController(mekamon_uart)
    motion_controller.pwn_mekamon()
    motion_controller.set_height("height,%d" % (config.default_height))
 
    # Setup complete. Start command and control server
    try: 
        logging.info("Setup complete. Waiting for network control messages...")
        is_running = True 

        while is_running:
            data, addr = serverSock.recvfrom(1024)
            logging.info("Received client message: %s" % (data))

            if 'exit' in data.lower():
                logging.info("Exiting...")
                is_running = False
            elif 'motion' in data.lower():
                motion_controller.xyz_motion(data)
            elif 'height' in data.lower():
                motion_controller.set_height(data)
            elif 'raw' in data.lower():
                motion_controller.raw_motion(data)
            else:
                motion_controller.turn_motion()
                motion_controller.stop_motion()

    finally:
        logging.info("Disconnecting BLE from Mekamon")
        mekamon_device.disconnect()

 
# Get the BLE provider for the current platform.
ble = Adafruit_BluefruitLE.get_provider()
 
# Initialize the BLE system.  MUST be called before other BLE calls!
ble.initialize()

# Initialize global mekamon device
# Use this to safely disconnect device with KeyboardInterrupt
mekamon_device = None
 
# Start the mainloop to process BLE events, and run the provided function in
# a background thread.  When the provided main function stops running, returns
# an integer status code, or throws an error the program will exit.
ble.run_mainloop_with(main)

