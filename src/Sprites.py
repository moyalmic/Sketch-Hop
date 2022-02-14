import pygame as pg
import os
import random
import numpy as np
from Constants import *

vector = pg.math.Vector2


# Class for displaying images
class Image(pg.sprite.Sprite):
    def __init__(self, pos_x, pos_y, image):
        pg.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = pos_x
        self.rect.y = pos_y


# Class for loading and parsing spritesheets
class Spritesheet:
    def __init__(self, image):
        self.spritesheet = image

    # Grab image out of a larger spritesheet
    def get_image(self, x, y, width, height):
        image = pg.surface.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        return image


# Class that holds the main character
class Character(pg.sprite.Sprite):
    def __init__(self, pos_x, pos_y, game, charType):
        self.set_character_sprites(charType)
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.runSheet = Spritesheet(self.characterRun)
        self.idleSheet = Spritesheet(self.characterIdle)
        self.jump_frame_r = self.characterJump
        self.jump_frame_l = pg.transform.flip(self.jump_frame_r, True, False)
        self.fall_frame_r = self.characterFall
        self.fall_frame_l = pg.transform.flip(self.fall_frame_r, True, False)
        self.load_images()
        self.image = self.standing_frames_r[0]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        # Movement variables
        self.boosted = False
        self.pos = vector(pos_x, pos_y)
        self.vel = vector(0, 0)
        self.acc = vector(0, 0)
        # Animation variables
        self.facing_right = False
        self.running = False
        self.jumping = False
        self.falling = False
        self.current_frame = 0
        self.last_update = 0

    # Fixed different character loading to be parametrized
    def set_character_sprites(self, charType):
        self.assets = os.path.join(os.path.dirname(__file__), '../sprites/Main Characters')
        if charType == 1:
            self.assets = os.path.join(self.assets, 'Pink Man')
            self.characterRun = pg.image.load(os.path.join(self.assets, 'Run (46x50).png'))
            self.characterIdle = pg.image.load(os.path.join(self.assets, 'Idle (46x54).png'))
            self.characterJump = pg.image.load(os.path.join(self.assets, 'Jump (46x58).png'))
            self.characterFall = pg.image.load(os.path.join(self.assets, 'Fall (46x54).png'))
            self.PLAYER_WIDTH_IDLE = 46
            self.PLAYER_HEIGHT_IDLE = 54
            self.PLAYER_WIDTH_RUNNING = 46
            self.PLAYER_HEIGHT_RUNNING = 50
        elif charType == 2:
            self.assets = os.path.join(self.assets, 'Mask Dude')
            self.characterRun = pg.image.load(os.path.join(self.assets, 'Run (52x56).png'))
            self.characterIdle = pg.image.load(os.path.join(self.assets, 'Idle (48x60).png'))
            self.characterJump = pg.image.load(os.path.join(self.assets, 'Jump (48x64).png'))
            self.characterFall = pg.image.load(os.path.join(self.assets, 'Fall (50x60).png'))
            self.PLAYER_WIDTH_IDLE = 48
            self.PLAYER_HEIGHT_IDLE = 60
            self.PLAYER_WIDTH_RUNNING = 52
            self.PLAYER_HEIGHT_RUNNING = 56

    def load_images(self):
        # Idle frames facing right
        self.standing_frames_r = list()
        for frame in range(10):
            self.standing_frames_r.append(
                self.idleSheet.get_image(frame * self.PLAYER_WIDTH_IDLE, 0, self.PLAYER_WIDTH_IDLE,
                                         self.PLAYER_HEIGHT_IDLE))
        for frame in self.standing_frames_r:
            frame.set_colorkey(BLACK)

        # Idle frames facing left
        self.standing_frames_l = list()
        for frame in self.standing_frames_r:
            frame.set_colorkey(BLACK)
            self.standing_frames_l.append(pg.transform.flip(frame, True, False))

        # Running frames facing right
        self.running_frames_r = list()
        for frame in range(11):
            self.running_frames_r.append(
                self.runSheet.get_image(frame * self.PLAYER_WIDTH_RUNNING, 0, self.PLAYER_WIDTH_RUNNING,
                                        self.PLAYER_HEIGHT_RUNNING))
        for frame in self.running_frames_r:
            frame.set_colorkey(BLACK)

        # Running frames facing left
        self.running_frames_l = list()
        for frame in self.running_frames_r:
            frame.set_colorkey(BLACK)
            self.running_frames_l.append((pg.transform.flip(frame, True, False)))

    def update(self):
        self.animation()
        keys = pg.key.get_pressed()
        # Gravity
        self.acc = vector(0, PLAYER_GRAV)
        # Handle key inputs
        if keys[pg.K_LEFT]:
            self.acc.x = -PLAYER_ACC
        if keys[pg.K_RIGHT]:
            self.acc.x = PLAYER_ACC

        # Calculations to move player
        self.acc.x += self.vel.x * PLAYER_FRICT
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        # Check if player is out of bounds
        if self.pos.x < 16:
            self.pos.x = 16
        elif self.pos.x > WIN_WIDTH - 16:
            self.pos.x = WIN_WIDTH - 16

        self.rect.midbottom = self.pos

    def animation(self):
        now = pg.time.get_ticks()
        if abs(self.vel.x) < 0.3:
            self.running = False
        elif self.vel.x > 0:
            self.running = True
            self.facing_right = True
        elif self.vel.x < 0:
            self.running = True
            self.facing_right = False
        if abs(self.vel.y) < 0.2:
            self.boosted = False
            self.jumping = False
            self.falling = False
        elif self.vel.y < 0:
            self.jumping = True
        elif self.vel.y > 0:
            self.falling = True

        # Jumping image
        if self.jumping:
            if now - self.last_update > FPS:
                if self.facing_right:
                    self.last_update = now
                    self.image = self.jump_frame_r
                else:
                    self.last_update = now
                    self.image = self.jump_frame_l

        # Falling image
        elif self.falling:
            if now - self.last_update > FPS:
                if self.facing_right:
                    self.last_update = now
                    self.image = self.fall_frame_r
                else:
                    self.last_update = now
                    self.image = self.fall_frame_l

        # Idle animation
        elif not self.running and not self.jumping:
            if now - self.last_update > FPS:
                if self.facing_right:
                    self.last_update = now
                    self.current_frame = (self.current_frame + 1) % len(self.standing_frames_r)
                    self.image = self.standing_frames_r[self.current_frame]
                else:
                    self.last_update = now
                    self.current_frame = (self.current_frame + 1) % len(self.standing_frames_l)
                    self.image = self.standing_frames_l[self.current_frame]

        # Running animation
        elif self.running and not self.jumping:
            if now - self.last_update > FPS / 2:
                if self.facing_right:
                    self.last_update = now
                    self.current_frame = (self.current_frame + 1) % len(self.running_frames_r)
                    self.image = self.running_frames_r[self.current_frame]
                else:
                    self.last_update = now
                    self.current_frame = (self.current_frame + 1) % len(self.running_frames_l)
                    self.image = self.running_frames_l[self.current_frame]

    def jump_cut(self):
        if self.jumping:
            if self.vel.y < - 10:
                self.vel.y = - 10

    def jump(self):
        self.rect.x += 2
        hits = pg.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.x -= 2
        if hits and not self.jumping:
            self.jumping = True
            self.vel.y = -PLAYER_JUMP
            self.game.jump_sound.play()


# Class that holds platforms
class Platform(pg.sprite.Sprite):
    def __init__(self, x, y, image, game):
        self.groups = game.platforms
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        if random.randrange(101) < POW_FREQ:
            Powerup(self.game, self)


# Class that holds power ups, right now just trampolines
class Powerup(pg.sprite.Sprite):
    def __init__(self, game, plat):
        self.groups = game.powerups
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.plat = plat
        self.image = trampolineIdle
        self.rect = self.image.get_rect()
        self.rect.midbottom = self.plat.rect.midtop
        self.idle = True

    def update(self):
        if not self.game.platforms.has(self.plat):
            self.kill()
