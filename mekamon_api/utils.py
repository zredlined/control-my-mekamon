#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utilities for Mekamon control API
"""

__author__      = "Alex Watson"
__copyright__   = "Copyright 2019"

import binascii
import logging
import time

from cobs import cobs
from struct import pack

import config

def execute_cmds(cmd_array, mekamon_uart, desc=config.default_cmd_desc):
    """
    Wrapper for execute_cmd that processes a list of commands in sequence

    Args: numpy.array of type data (byte string)
    Returns: None
    """
    for index, cmd in enumerate(cmd_array):
        cmd_desc = "%s message [%d/%d]" % (desc, index, len(cmd_array))
        execute_cmd(cmd, mekamon_uart, desc=cmd_desc)

def execute_cmd(cmd, mekamon_uart, desc=config.default_cmd_desc): 
    """
    Generates and writes a command directly to the Mekamon UART

    Args: data (byte string)
    Returns: None
    """
    msgOut = generate_cmd(cmd)
    logging.info("  -- %s: [%s]" % (desc, msgOut))
    msgOut = unhexlify(msgOut)
    mekamon_uart.write(msgOut)
    time.sleep(config.message_delay) 

def unhexlify(hexstr):
    """
    Return the binary data represented by the hexadecimal string hexstr. 
    This function is the inverse of b2a_hex(). 

    Args: hexstr (even number of decimal digits)
    Returns: binary data
    """
    return binascii.unhexlify(hexstr)

def calc_checksum(cmd):
    """
    Method to calculate BLE/UART message checksums for Mekamon

    Args: data (byte string) message for Mekamon
    Returns: integer checksum
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

    Generate_cmd produces hex for Mekamon command from signed int inputs
    using the consistent overhead byte stuffing method (COBS)

    Examples: 
        generate_cmd([6, strafe, fwd, turn]) # 6=motion
        generate_cmd([6,0,0,0]) # 02060101010c00

    Args: list of integers
    Returns: string of hexadecimal representation of binary data (str)
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

def interpolate_range(a,b,s=5):
    """ Generate consecutive values list between two numbers with optional step (default=5)."""
    if (a == b):
        return [a]
    else:
        mx = max(a,b)
        mn = min(a,b)
        result = []
        # inclusive upper limit. If not needed, delete '+1' in the line below
        while(mn < mx + 1):
            # if step is positive we go from min to max
            if s > 0:
                result.append(mn)
                mn += s
            # if step is negative we go from max to min
            if s < 0:
                result.append(mx)
                mx += s
        return result

