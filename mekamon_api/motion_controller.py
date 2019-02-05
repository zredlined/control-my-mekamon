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
from utils import generate_cmd, unhexlify, execute_cmds, execute_cmd, interpolate_range

class MotionController(object):

    """
    Class to support initializing and controlling Mekamon via BLE

    Args:
    Returns:
    """
   
    def __init__(self, mekamon_uart):
        self.mekamon_uart = mekamon_uart
        self.current_height = config.default_height

    def pwn_mekamon(self):
        # list of initial MM messages.
        execute_cmds(config.pwn_mekamon_list, self.mekamon_uart, desc="Pwning Mekamon")

    def xyz_motion(self, message):
        """
        Input command: [6,fwd,strafe,turn]
        fwd = -128-127 # signed byte
        strafe = -128-127 # signed byte
        turn = -128-127 # signed byte
        """
        values = message.split(',') 

        cmd_type = int(values[1])
        fwd = int(values[2])
        strafe = int(values[3])
        turn = int(values[4])
    
        assert cmd_type== 6 # 6 == motion
        assert fwd < 128 and fwd >= -128 
        assert strafe < 128 and strafe >= -128 
        assert turn < 128 and turn >= -128 
     
        cmd = [cmd_type,
               fwd,
               strafe,
               turn
               ]

        execute_cmd(cmd, self.mekamon_uart, desc="Motion")

    def raw_motion(self, message):
        values = message.split(',') 
        desc = values[0]
        cmd = [int(x) for x in values[1:]] 
        execute_cmd(cmd, self.mekamon_uart, desc=desc)

    def set_height(self, message):
        """
        Example: ["height",127]
        desired_height range [0...127]
        """
        values = message.split(',') 
     
        # extract commmand attributes
        desired_height = int(values[1])
        assert desired_height < 128 and desired_height > 0 

        cmd = [4,0,7,desired_height]
        execute_cmd(cmd, self.mekamon_uart, desc="Height")
 
        """
        # TODO needs work to smooth out motion. 
        # Linear interpolation still jolty
        if desired_height > self.current_height:
            for x in interpolate_range(self.current_height, desired_height, 15):
                cmd = [4,0,7,x]
                execute_cmd(cmd, self.mekamon_uart, desc="Rising")
        else:
            for x in interpolate_range(desired_height, self.current_height, -15):
                cmd = [4,0,7,x]
                execute_cmd(cmd, self.mekamon_uart, desc="Lowering")
        """

        # update current height
        self.current_height = desired_height 
            
