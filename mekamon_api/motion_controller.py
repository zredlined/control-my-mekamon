#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Keyboard controller for Mekamon robot
"""

__author__      = "Alex Watson"
__copyright__   = "Copyright 2018"

import logging
import sys
import time

import Adafruit_BluefruitLE
from Adafruit_BluefruitLE.services import UART, DeviceInformation

import config
from utils import generate_cmd, unhexlify, execute_cmds, execute_cmd

class MotionController(object):

    """
    Class to support initializing and controlling Mekamon via BLE

    Args:
    Returns:
    """
   
    def __init__(self, mekamon_uart):
        self.mekamon_uart = mekamon_uart

    def pwn_mekamon(self):
        # list of initial MM messages.
        execute_cmds(config.pwn_mekamon_list, self.mekamon_uart, desc="Pwning Mekamon")

    def xyz_motion(self, message):
        values = message.split(',') 
     
        cmd = [int(values[1]), 
               int(values[2]), 
               int(values[3]), 
               int(values[4])
               ] # 6=motion

        execute_cmd(cmd, self.mekamon_uart, desc="Motion")

    def stop_motion(self):
        cmd = [6, 0, 0, 0] # 6=motion
        execute_cmd(cmd, self.mekamon_uart, desc="Stopping Mekamon")
        
    def turn_motion(self):
        #limit = 80 # max +/- 127
        strafe = 0
        fwd = 0 
        turn = 80
        desc = "Turning Mekamon"
     
        logging.info('%s -- strafe: %d fwd: %d turn: %d' % (desc, strafe, fwd, turn))
        cmd = [6, strafe, fwd, turn] # 6=motion
        execute_cmd(cmd, self.mekamon_uart, desc=desc)


