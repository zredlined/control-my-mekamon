#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Keyboard controller for Mekamon robot
"""

__author__      = "Alex Watson"
__copyright__   = "Copyright 2018"

import logging
import sys

import pygame

pygame.init()
screen = pygame.display.set_mode((720, 480))

class Mekamon(pygame.sprite.Sprite):

    def __init__(self):
        super(Mekamon, self).__init__()
        self.rect = pygame.Rect((0, 0), (32, 32))
        self.image = pygame.Surface((32, 32))
        self.image.fill((255, 255, 255))
        self.velocity = [0, 0]  # It's current velocity.
        self.speed = 4  # The speed the mekamon will move.
        self.dx = []  # Keeps track of the horizontal movement.
        self.dy = []  # Keeps track of the vertical movement.

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

        if mekamon.dx != [] or mekamon.dy != []:
            logging.info("strafe:%s fwd:%s turn:%s" % (mekamon.dx, mekamon.dy, 0)) 

if __name__ == '__main__':
    main()

