import pygame as pg
import pygame_menu as pgmenu
import os
import sys
import math
import random
import Sprites
from Constants import *

charType = 1


class Menu:
    def __init__(self):
        self.theme = pgmenu.themes.THEME_ORANGE
        self.theme.menubar_close_button = False
        self.menu = pgmenu.Menu(GAME_NAME, WIN_WIDTH, WIN_HEIGHT, theme=self.theme)
        self.menu.add.image("../sprites/Other/Title.png", align=pgmenu.locals.ALIGN_CENTER)
        self.menu.add.image("../sprites/Main Characters/Pink Man/Jump (46x58).png", angle=10)
        self.menu.add.vertical_margin(100)

    def add_button(self, text, function):
        self.menu.add.button(text, function, font_size=50)

    def mainloop(self, window):
        self.menu.mainloop(window)


class Game:
    # Initialize the game window
    def __init__(self):
        pg.init()
        self.sprites = dict()
        self.window = pg.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        pg.display.set_caption("Sketch Hop")
        self.clock = pg.time.Clock()
        os.environ["SDL_VIDEO_CENTERED"] = "1"
        self.running = True
        self.font_name = pg.font.match_font(FONT_NAME)
        self.convert_sprites()
        self.dir = os.path.dirname(__file__)
        self.sounds = os.path.join(self.dir, '../sounds')
        self.jump_sound = pg.mixer.Sound(os.path.join(self.sounds, 'jump_sound.mp3'))
        self.game_over_sound = pg.mixer.Sound(os.path.join(self.sounds, 'game_over.wav'))
        self.new_game_sound = pg.mixer.Sound(os.path.join(self.sounds, 'new_game.wav'))
        self.trampoline_sound = pg.mixer.Sound(os.path.join(self.sounds, 'trampoline_sound.mp3'))

    # Starts a new game
    def new(self):
        self.new_game_sound.play()
        self.score = 0
        self.images = pg.sprite.Group()
        self.images.add(Sprites.Image(50, WIN_HEIGHT - 250, self.sprites.get("quip")))
        self.powerups = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        Sprites.Platform(0, WIN_HEIGHT - 92, self.sprites.get("basePlatform"), self)
        Sprites.Platform(50, WIN_HEIGHT - MAX_JUMP, self.sprites.get("woodenPlatform"), self)
        Sprites.Platform(WIN_WIDTH - PLAT_WIDTH * 7, WIN_HEIGHT - MAX_JUMP - 192 + PLAT_HEIGHT + 1,
                         self.sprites.get("woodenPlatform"), self)
        Sprites.Platform(WIN_WIDTH, WIN_HEIGHT / 4 + 190, self.sprites.get("woodenPlatform"), self)
        Sprites.Platform(200, WIN_HEIGHT / 4, self.sprites.get("woodenPlatform"), self)
        self.mainCharater = Sprites.Character(WIN_WIDTH - 150, 500, self, charType)
        self.run()

    # Main game loop
    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.window.blit(background, (0, 0))
            self.handle_events()
            self.update()
            self.draw()
        self.show_game_over()

    # Calculations to update positions
    def update(self):
        self.platforms.update()
        self.powerups.update()
        self.mainCharater.update()
        # Checks for collisions
        if self.mainCharater.vel.y > 0:
            hits = pg.sprite.spritecollide(self.mainCharater, self.platforms, False)
            if hits:
                lowest = hits[0]
                for hit in hits:
                    if hit.rect.bottom > lowest.rect.bottom:
                        lowest = hit
                if lowest.rect.right + 15 > self.mainCharater.pos[0] > lowest.rect.left - 15:
                    if self.mainCharater.pos.y < lowest.rect.bottom:
                        self.mainCharater.pos.y = lowest.rect.top + 1
                        self.mainCharater.vel.y = 0

        # If player hits a powerup
        pow_hits = pg.sprite.spritecollide(self.mainCharater, self.powerups, False)
        for pow in pow_hits:
            if self.mainCharater.vel.y >= 0:
                self.trampoline_sound.play()
                self.mainCharater.vel.y = -BOOST_POWER
                self.mainCharater.jumping = False
                self.mainCharater.boosted = True
        # Player reaching top of screen (check for window scrolling)
        if self.mainCharater.rect.top <= WIN_HEIGHT / 4:
            self.mainCharater.pos.y += max(abs(self.mainCharater.vel.y), 10)
            self.scroll_upwards(self.platforms)
            self.scroll_upwards(self.images)
            self.scroll_upwards(self.powerups)
        # Spawn new platforms above the screen in place of the old ones
        while len(self.platforms) < NUM_OF_PLATS:
            p = self.generate_platform()
            self.platforms.add(p)
        # Check for game over
        if self.mainCharater.rect.top > WIN_HEIGHT:
            self.playing = False

    # Handle input
    def handle_events(self):
        for e in pg.event.get():
            if e.type == pg.QUIT:
                if self.playing:
                    sys.exit()
            if e.type == pg.KEYDOWN:
                if e.key == pg.K_SPACE or e.key == pg.K_UP:
                    self.mainCharater.jump()
            if e.type == pg.KEYUP:
                if e.key == pg.K_SPACE or e.key == pg.K_UP:
                    if not self.mainCharater.boosted:
                        self.mainCharater.jump_cut()

    # Draw everything to the screen
    def draw(self):
        self.platforms.draw(self.window)
        self.powerups.draw(self.window)
        self.images.draw(self.window)
        self.window.blit(self.mainCharater.image, self.mainCharater.rect.topleft)
        self.draw_text("Score: " + str(self.score), 35, 15, 15, mode="topleft")
        pg.display.update()

    # Show the main menu
    def show_main_menu(self):
        self.menu = Menu()
        self.menu.add_button('Play', self.new)
        self.menu.add_button('Quit', pgmenu.events.EXIT)
        self.menu.mainloop(self.window)

    # Show the game over screen
    def show_game_over(self):
        if self.running:
            self.window.blit(background, (0, 0))
            self.draw_text("Your score was: " + str(self.score), 75, WIN_WIDTH / 2, (WIN_HEIGHT / 2))
            self.draw_text("Press any key to return to main menu", 35, WIN_WIDTH / 2, WIN_HEIGHT - 200)
            self.game_over_sound.play()
            pg.display.update()
            self.wait_for_input()

    # Scrolls all of the sprites in entities up according to the players speed
    def scroll_upwards(self, entities):
        for item in entities:
            item.rect.y += max(abs(self.mainCharater.vel[1]), 2)
            if item.rect.top >= WIN_HEIGHT:
                item.kill()
                self.score += 10

    # Draws text to the screen
    def draw_text(self, text, size, x, y, mode="center"):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, (0, 0, 0))
        text_rect = text_surface.get_rect()
        if mode == "topleft":
            text_rect.topleft = (x, y)
        else:
            text_rect.center = (x, y)
        self.window.blit(text_surface, text_rect)

    # Pause function
    def wait_for_input(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                elif event.type == pg.KEYDOWN:
                    waiting = False

    # Converts images to correct mode
    def convert_sprites(self):
        self.sprites["basePlatform"] = basePlatform.convert_alpha()
        self.sprites["woodenPlatform"] = woodenPlatform.convert_alpha()
        self.sprites["quip"] = quip.convert_alpha()
        self.sprites["background"] = background.convert_alpha()

    # Generates a platform within jumping distance of at least one other platform
    def generate_platform(self):
        generate = True
        while generate:
            far_enough = True
            close_enough = False
            pos_x = random.randrange(0, WIN_WIDTH - PLAT_WIDTH, 5)
            pos_y = random.randrange(int((-MAX_JUMP * 2) + PLAT_HEIGHT), -PLAT_HEIGHT, 5)
            # Check if i'm within jumping distance of one other platform
            distance = 0
            for plat in self.platforms:
                distance = self.calculate_distance(pos_x, pos_y, plat)
                if distance < MAX_JUMP - 50:
                    close_enough = True
                if distance < 150:
                    far_enough = False
                    break
            if far_enough and close_enough:
                generate = False
        return Sprites.Platform(pos_x, pos_y, self.sprites["woodenPlatform"], self)

    # Calculates the distance between midtop points of two sprites
    def calculate_distance(self, x, y, sprite2):
        sp2 = sprite2.rect.midtop
        distance = math.sqrt((sp2[0] - x) ** 2 + (sp2[1] - y) ** 2)
        return distance


if __name__ == '__main__':
    if len(sys.argv) > 2:
        print("Too many arguments. Expected 1 or 2 (Second argument is character type)")
        sys.exit()
    if len(sys.argv) == 2:
        if int(sys.argv[1]) == 1:
            charType = 1
        elif int(sys.argv[1]) == 2:
            charType = 2

    game = Game()
    while game.running:
        game.show_main_menu()
