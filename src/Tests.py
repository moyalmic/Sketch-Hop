import pytest
import main
import Sprites
import pygame as pg
import random
import math
from Constants import *

vector = pg.math.Vector2

MAX_JUMP = 450


class Character(pg.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        pg.sprite.Sprite.__init__(self)
        self.pos = vector(pos_x, pos_y)
        self.vel = vector(0, 0)
        self.acc = vector(0, 0)
        self.rect = pg.rect.Rect(pos_x, pos_y, 50, 50)


class Platform(pg.sprite.Sprite):
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        self.pos = vector(x, y)
        self.rect = pg.rect.Rect(x, y, 50, 50)


@pytest.fixture
def character_one() -> Character:
    return Character(WIN_WIDTH / 2, WIN_HEIGHT / 2)


@pytest.fixture
def platforms_one() -> Platform:
    platforms = pg.sprite.Group()
    platforms.add(Platform(0, 150))
    platforms.add(Platform(WIN_WIDTH / 2, WIN_HEIGHT / 2))
    platforms.add(Platform(0, WIN_HEIGHT - 100))
    return platforms


@pytest.fixture
def platforms_two():
    return [Platform(300, 300), Platform(800, 800)]


@pytest.fixture
def character_two() -> Character:
    return Character(300, 500)


@pytest.fixture
def platforms_three():
    platforms = pg.sprite.Group()
    platforms.add(Platform(300, 500))
    return platforms


@pytest.fixture
def character_three() -> Character:
    return Character(400, 400)


@pytest.fixture
def platforms_four():
    platforms = pg.sprite.Group()
    platforms.add(Platform(425, 500))
    return platforms


@pytest.fixture
def platforms_five():
    platforms = pg.sprite.Group()
    platforms.add(Platform(200, 350))
    platforms.add(Platform(865, 321))
    return platforms


# Simulation of update function dummed down for testing purposes
# (Avoiding keyboard input)
def move_character(character, direction):
    if direction == "left":
        character.acc.x = -PLAYER_ACC
    elif direction == "right":
        character.acc.x = PLAYER_ACC

    # Calculations to move player
    character.acc.x += character.vel.x * PLAYER_FRICT
    character.vel += character.acc
    character.pos += character.vel + 0.5 * character.acc

    # Check if player is out of bounds
    if character.pos.x < 16:
        character.pos.x = 16
    elif character.pos.x > WIN_WIDTH - 16:
        character.pos.x = WIN_WIDTH - 16


# Simualtion of screen scrolling function dummed down for testing purposes
# Scrolls by 100 pixels in this simulation
def scroll_screen(items):
    for item in items:
        item.pos.y += 100
        if item.pos.y >= WIN_HEIGHT:
            item.kill()


# Simulation of platform generation algorithm
def generate_platform(platforms):
    generate = True
    while generate:
        far_enough = True
        close_enough = False
        pos_x = random.randrange(0, WIN_WIDTH, 5)
        pos_y = random.randrange(0, WIN_HEIGHT, 5)
        # Check if i'm within jumping distance of one other platform
        distance = 0
        for plat in platforms:
            distance = calculate_distance(pos_x, pos_y, plat.pos.x, plat.pos.y)
            if distance < MAX_JUMP:
                close_enough = True
            if distance < 150:
                far_enough = False
                break
        if far_enough and close_enough:
            generate = False
    return Platform(pos_x, pos_y)


def calculate_distance(x1, y1, x2, y2):
    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return distance


# Tests character movement
def test_character_update1(character_one, direction="left"):
    move_character(character_one, direction)
    assert character_one.pos.x == (WIN_WIDTH / 2) - 1.5


def test_character_update2(character_one, direction="right"):
    for i in range(100):
        move_character(character_one, direction)
    assert character_one.pos.x == WIN_WIDTH - 16


def test_character_update3(character_one):
    for i in range(5):
        move_character(character_one, "right")
    character_one.vel = vector(0, 0)
    character_one.acc = vector(0, 0)
    for i in range(5):
        move_character(character_one, "left")
    assert character_one.pos.x == WIN_WIDTH / 2


# Scrolls two platforms off the screen, killing them
def test_platform_count1(platforms_one):
    for i in range(5):
        scroll_screen(platforms_one)
    assert platforms_one.spritedict.__len__() == 1


# Tests if generated platform is far enough from all other platforms
def test_platform_spawning1(platforms_two):
    platforms_two.append(generate_platform(platforms_two))
    assert calculate_distance(platforms_two[0].pos.x, platforms_two[0].pos.y, platforms_two[2].pos.x,
                              platforms_two[2].pos.y) > 150
    assert calculate_distance(platforms_two[1].pos.x, platforms_two[1].pos.y, platforms_two[2].pos.x,
                              platforms_two[2].pos.y) > 150


# Tests collision detection (They do collide)
def test_collision_detection1(character_two, platforms_three):
    hits = pg.sprite.spritecollide(character_two, platforms_three, False)
    assert hits[0]


def test_collision_detection2(character_three, platforms_four):
    character_three.rect = pg.rect.Rect(400, 400, 50, 200)
    hits = pg.sprite.spritecollide(character_three, platforms_four, False)
    assert hits[0]


# Tests collision detection (They don't collide)
def test_collision_detection3(character_one, platforms_five):
    hits = pg.sprite.spritecollide(character_one, platforms_five, False)
    assert len(hits) == 0
