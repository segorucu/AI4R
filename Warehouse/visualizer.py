######################################################################
# This file copyright the Georgia Institute of Technology
#
# Permission is given to students to use or modify this file (only)
# to work on their assignments.
#
# You may NOT publish this file or make it available to others not in
# the course.
#
######################################################################

import time
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame

from pygame.locals import (
    K_SPACE,
    K_m,
    KEYDOWN,
    QUIT,
)

FRAME_RATE_PER_SECOND = 1
# Speed Reference (ymmv)
# 0: 'MANUAL-PAUSE'
# 1: 'SNAIL'
# 2: 'TURTLE'
# 3: 'HARE'
# 4: 'CHEETAH'
# 5: 'FALCON'

PAUSE_AT_END_FOR_X_SECONDS = 1

# colors needed for the gui background/text
BLACK = pygame.Color('Black')
WHITE = pygame.Color('White')
BOX_BROWN = pygame.Color(217, 148, 78)

IMGS = {
    'wall'          : 'viz/wall.png',
    'traversable'   : 'viz/traversable.png',
    'robot'         : 'viz/robot.png',
    'robot_with_box': 'viz/robot_with_box.png',
    'box'           : 'viz/box.png',
    'dropzone'      : 'viz/dropzone.png',
    'jay'           : 'viz/jaybot.png',
    'mask'          : 'viz/mask.png',
}

WAREHOUSE_LEGEND = {
    '*': 'robot',
    '#': 'wall',
    '.': 'traversable',
    '@': 'dropzone',
    '*+box': 'robot_with_box',
}

########################################################################
# If you're here, good job on reading/looking at the code!
# This flag was introduced last year, hopefully it won't
# be necessary much longer.  Toggle for permanent safety or
# use the keyboard shortcut m while the visualization is running.
########################################################################
MASK_FLAG = False


class GUI:
    pygame.init()
    BORDER = 50
    CELL_HEIGHT = 100
    CELL_WIDTH = 100
    FONT_SIZE = 20
    FONT = pygame.font.Font('freesansbold.ttf', FONT_SIZE)
    CELL_SIZE = CELL_HEIGHT, CELL_WIDTH

    def __init__(self, state, total_num_actions):
        self.total_actions_left = total_num_actions+1
        self.grid = state.warehouse_state
        self.boxes_delivered = []
        self.grid_num_rows = len(self.grid)
        self.grid_num_cols = len(self.grid[0])
        self.screen_height = (self.grid_num_rows * self.CELL_HEIGHT) + (2 * self.BORDER)
        self.screen_width = (self.grid_num_cols * self.CELL_WIDTH) + (2 * self.BORDER)

        self.screen = pygame.display.set_mode([self.screen_width, self.screen_height])
        self.update(state)

    def update(self, state):
        global MASK_FLAG
        self.total_actions_left -= 1
        self.grid = state.warehouse_state
        box_held = state.box_held
        dropzone = state.dropzone
        robot_position = state.robot_position
        total_cost = state.total_cost

        delivered_box = len(state.boxes_delivered) > len(self.boxes_delivered)
        self.boxes_delivered = state.boxes_delivered[:]

        self.screen.fill(WHITE)
        self.update_bot()

        # draw warehouse sprites
        for r in range(self.grid_num_rows):
            for c in range(self.grid_num_cols):
                x = self.BORDER + c * self.CELL_WIDTH
                y = self.BORDER + r * self.CELL_HEIGHT
                grid_symbol = self.grid[r][c]
                self.draw_sprite('.', x, y)

                if grid_symbol == '*':
                    if robot_position == dropzone:
                        self.draw_sprite('@', x, y)
                    if box_held:
                        grid_symbol += '+box'
                self.draw_sprite(grid_symbol, x, y)
                if grid_symbol == '@' and delivered_box:
                    self.draw_sprite('remove_box', x, y)

        # draw game msgs
        cost_msg = f'Cost: {total_cost}'
        text = self.FONT.render(cost_msg, True, BLACK)
        self.screen.blit(text, (self.BORDER, self.BORDER - self.BORDER // 2))

        delivered_msg = f'Delivered: {self.boxes_delivered}'
        text = self.FONT.render(delivered_msg, True, BLACK)
        self.screen.blit(text, (self.BORDER, self.screen_height - self.BORDER + 10))

        action_msg = f'Actions Left: {self.total_actions_left}'
        text = self.FONT.render(action_msg, True, BLACK)
        self.screen.blit(text, (self.BORDER, 0))

        # render new display
        pygame.display.update()

        # game event loop
        pause = True if FRAME_RATE_PER_SECOND == 0 else False
        quit_signal = False
        game_play=True
        while game_play:
            game_play = pause
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        pause = False
                    elif event.key == K_m:
                        MASK_FLAG = not MASK_FLAG
                if event.type == QUIT:
                    pause = False
                    quit_signal = True

        # initiate wait
        if FRAME_RATE_PER_SECOND:
            time.sleep( 1 / FRAME_RATE_PER_SECOND )

        if self.total_actions_left == 0:
            time.sleep(PAUSE_AT_END_FOR_X_SECONDS)

        return quit_signal

    def draw_sprite(self, key, x, y):
        key_val = WAREHOUSE_LEGEND.get(key, 'box')
        img = pygame.image.load(IMGS[key_val])

        if key == 'remove_box':
            img = pygame.transform.scale(img, [i // 2 for i in self.CELL_SIZE]).convert_alpha()
            img.set_alpha(200)
            x += self.CELL_WIDTH // 4
            y += self.CELL_HEIGHT // 4
        else:
            img = pygame.transform.scale(img, self.CELL_SIZE).convert_alpha()

        self.screen.blit(img, (x, y))

        # safety first
        if key == '*' and MASK_FLAG:
            img = pygame.image.load(IMGS['mask'])
            img = pygame.transform.scale(img, (self.CELL_WIDTH // 2, self.CELL_HEIGHT // 5)).convert_alpha()
            x += self.CELL_WIDTH // 4
            y += int(self.CELL_HEIGHT * .35)
            self.screen.blit(img, (x, y))

        # label box ID
        if key_val == 'box' and key != 'remove_box':
            text = self.FONT.render(key, True, BOX_BROWN)
            self.screen.blit(text, (x + self.CELL_WIDTH // 5, y + self.CELL_HEIGHT // 6))

    def update_bot(self):
        if self.boxes_delivered and self.boxes_delivered[-1] == 'J':
            WAREHOUSE_LEGEND['*'] = 'jay'
        else:
            WAREHOUSE_LEGEND['*'] = 'robot'

    def quit(self):
        pygame.quit()
