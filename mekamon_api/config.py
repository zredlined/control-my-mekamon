#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
config.py
Configuration settings for Mekamon control
"""

__author__      = "Alex Watson"
__copyright__   = "Copyright 2019"

import numpy as np

# Replay these messages to take control of the Mekamon
init_cmd_1 = [16] # 02101300
init_cmd_2 = [7,1] # 0307010c00
stop_motion_cmd = [6,0,0,0] # 02060101010c00
pwn_mekamon_list= np.array([init_cmd_1, init_cmd_2, stop_motion_cmd])

# text messages
default_cmd_desc = "Executing command"

# BLE settings
message_delay = 0.5 # Time to sleep after sending message

# Server settings
# Here we define the UDP IP address as well as the port number that we have
# already defined in the client python script.
UDP_IP_ADDRESS = "192.168.4.2"
UDP_PORT_NO = 6789

