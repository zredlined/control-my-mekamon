#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utilities for Mekamon control API
"""

__author__      = "Alex Watson"
__copyright__   = "Copyright 2018"

import binascii
import logging
import time

from cobs import cobs
from struct import pack

import config

def execute_cmds(cmd_array, mekamon_uart, desc=config.default_cmd_desc):
    for index, cmd in enumerate(cmd_array):
        execute_cmd(cmd, mekamon_uart)

def execute_cmd(cmd, mekamon_uart, desc=config.default_cmd_desc): 
    msgOut = generate_cmd(cmd)
    msgOut = unhexlify(msgOut)
    logging.debug("  -- %s: [%s]" % (desc, msgOut))
    mekamon_uart.write(msgOut)
    time.sleep(0.5) 
    return True

def unhexlify(message):
    return binascii.unhexlify(message)

def calc_checksum(cmd):
    """
    Method to calculate BLE/UART message checksums for Mekamon

    Args:
    Returns:
    """

    ints = [ord(char) for char in cmd]
    checksum = sum(ints)
    checksum %= 256 # roll over if bigger than 8b max
    checksum ^= 256 # twos complement
    checksum += 1 # why add 1?
    checksum %= 256 # roll over if bigger than 8b max
    #logging.debug('checksum:',checksum)
    return checksum


def generate_cmd(int_sequence):
    """
    Method to generate raw commands for Mekamon robot

    Args:
    Returns:
        # generate_cmd produces hex for MM command from signed int inputs
        # this uses actual byte stuffing method
    """

    #logging.debug('int_sequence:', int_sequence)

    # build the command, append vars in hex string '\xff' format
    cmd = ''
    for x in int_sequence:
        cmd += pack('b',x) # b means treat as signed +- 128

    #logging.debug('cmd string:', cmd)

    # COBS before the checksum and terminal byte
    cmd = cobs.encode(cmd)
    #logging.debug('cobs encode: ', cmd)

    # checksum
    checksum = calc_checksum(cmd)
    cmd += chr(checksum) # chr hexifies 0-255

    # terminator
    cmd += chr(0)

    # convert to hex literal string without \x
    cmd = binascii.hexlify(cmd)

    return cmd

