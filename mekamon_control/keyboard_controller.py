#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Keyboard controller for Mekamon robot
"""

__author__      = "Alex Watson"
__copyright__   = "Copyright 2018"

import logging
import socket
import sys
import time

import pygame

import config

pygame.init()
screen = pygame.display.set_mode((config.screen_x, config.screen_y))

class Mekamon(pygame.sprite.Sprite):

    def __init__(self):
        super(Mekamon, self).__init__()

        # place initial sprite position
        offset_x = int(config.screen_x * .5)
        offset_y = int(config.screen_y * .8)
        self.rect = pygame.Rect((0+offset_x, 0+offset_y), 
                                (32+offset_x, 32+offset_y))
        self.image = pygame.Surface((32, 32))
        self.image.fill((255, 255, 255))
        self.velocity = [0, 0]  # It's current velocity.
        self.speed = config.mekamon_speed  # The speed the mekamon will move.
        self.dx = []  # Keeps track of the horizontal movement.
        self.dy = []  # Keeps track of the vertical movement.
        self.turn = []  # Keeps track of the vertical movement.

    def update(self):
        try:
            self.rect.x += self.dx[0]  # Index error if the list is empty.
        except IndexError:
            self.rect.x += 0
        try:
            self.rect.y += self.dy[0]  # Index error if the list is empty.
        except IndexError:
            self.rect.y += 0


def main():

    # Set up logging
    logging_format = '%(asctime)s : %(filename)s : %(levelname)s : %(message)s'
    logging_level = logging.INFO
    logging.basicConfig(format=logging_format, level=logging_level)
    logging.info("Running %s", " ".join(sys.argv))

    mekamon = Mekamon()
    is_mekamon_moving = True

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise SystemExit
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    mekamon.dx.insert(0, -mekamon.speed)
                elif event.key == pygame.K_d:
                    mekamon.dx.insert(0, mekamon.speed)
                elif event.key == pygame.K_w:
                    mekamon.dy.insert(0, -mekamon.speed)
                elif event.key == pygame.K_s:
                    mekamon.dy.insert(0, mekamon.speed)
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    mekamon.dx.remove(-mekamon.speed)
                elif event.key == pygame.K_d:
                    mekamon.dx.remove(mekamon.speed)
                elif event.key == pygame.K_w:
                    mekamon.dy.remove(-mekamon.speed)
                elif event.key == pygame.K_s:
                    mekamon.dy.remove(mekamon.speed)

        mekamon.update()
        screen.fill((0, 0, 0))
        screen.blit(mekamon.image, mekamon.rect)
        pygame.display.update()

        # Build mekamon command
        strafe = 0 if len(mekamon.dx) == 0 else mekamon.dx[0]
        fwd = 0 if len(mekamon.dy) == 0 else mekamon.dy[0]
        turn = 0 if len(mekamon.turn) == 0 else mekamon.turn[0]
        cmd = "motion,%s,%s,%s,%s" % (6, strafe, fwd, turn)

        if strafe == 0 and turn == 0 and fwd == 0 and is_mekamon_moving == True:
            clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            clientSock.sendto(cmd, (config.UDP_IP_ADDRESS, config.UDP_PORT_NO))
            logging.info("strafe:%s fwd:%s turn:%s cmd:%s" % (strafe, fwd, turn, cmd)) 
            is_mekamon_moving = False
            # Message delay to avoid flooding Mekamon with requests
            time.sleep(config.message_delay)
        elif not (strafe == 0 and turn == 0 and fwd == 0):
            # Send data to server
            clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            clientSock.sendto(cmd, (config.UDP_IP_ADDRESS, config.UDP_PORT_NO))
            logging.info("strafe:%s fwd:%s turn:%s cmd:%s" % (strafe, fwd, turn, cmd)) 
            is_mekamon_moving = True
            # Message delay to avoid flooding Mekamon with requests
            time.sleep(config.message_delay)


if __name__ == '__main__':
    main()

