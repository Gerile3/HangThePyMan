import os
from string import ascii_uppercase
import sys
from pathlib import Path
import pkg_resources

import pygame
import pygame.freetype

from words import random_word
from db_connection import db_connect


class Game:
    WIDTH = 800
    HEIGHT = 500
    RADIUS = 20
    GAP = 15
    GUESSED = ""
    HANGMAN_STATUS = 0
    WON = [False]
    DIR = Path(__file__).parent.absolute()

    def __init__(self):
        pygame.init()
        self.conn = db_connect(str(Game.DIR / "db" / "words.db"))
        self.word = random_word(self.conn)[1]
        self.game_font = pygame.freetype.Font(str(Game.DIR / "fonts" / "classic.TTF"), 26)
        self.word_font = pygame.freetype.SysFont("comicsans", 50)
        self.win = pygame.display.set_mode((Game.WIDTH, Game.HEIGHT))
        self.caption = pygame.display.set_caption("HangThePyMan")
        self.gameIcon = pygame.image.load(str(Game.DIR / "icon" / "icon.png"))
        self.replayIcon = pygame.image.load(str(Game.DIR / "icon" / "replay.png"))
        self.replayIcon = pygame.transform.scale(self.replayIcon, (50, 50))
        self.endIcon = pygame.image.load(str(Game.DIR / "icon" / "cross.png"))
        self.endIcon = pygame.transform.scale(self.endIcon, (50, 50))
        self.icon = pygame.display.set_icon(self.gameIcon)
        self.clock = pygame.time.Clock()
        self.b_color = (255, 255, 255)
        self.run = True
        self.images = self.load_images()
        self.letter_coordinates = self.load_buttons()
        self.state = "Title"
        self.play_btn = Button((37, 164, 206), 300, 150, 200, 100, "Play")
        self.quit_btn = Button((37, 164, 206), 300, 300, 200, 100, "Quit")
        self.replay_btn = Button((37, 164, 206), 315, 300, 50, 50, image=self.replayIcon, imagepos=(315, 300))
        self.end_btn = Button((37, 164, 206), 415, 300, 50, 50, image=self.endIcon, imagepos=(415, 300))
        try:
            self.version = pkg_resources.get_distribution("hangthepyman").version
        except Exception:
            self.version = "Beta"

    def load_images(self):
        images = []
        location = Game.DIR / "images"
        for i in range(len(os.listdir(location))):
            image = pygame.image.load(str(location / "hangman") + str(i) + ".png")
            images.append(image)
        return images

    def load_buttons(self):
        letter_coordinates = []
        start_x = round((Game.WIDTH - (Game.RADIUS * 2 + Game.GAP) * 13) / 2)
        start_y = 400
        for j in range(len(ascii_uppercase)):
            x = start_x + Game.GAP * 2 + ((Game.RADIUS * 2 + Game.GAP) * (j % 13)) - 15
            y = start_y + ((j // 13)) * (Game.GAP + Game.RADIUS * 2)
            letter_coordinates.append([x, y, ascii_uppercase[j], True])

        return letter_coordinates

    def draw(self):
        display_word = ""
        self.win.fill(self.b_color)

        if self.state == "Game":
            # draw word
            for letter in self.word:
                if letter in Game.GUESSED:
                    display_word += letter + " "
                else:
                    display_word += "_ "
            self.word_font.render_to(self.win, (400, 175), display_word, (0, 0, 0))

            # draw letters
            for letter in self.letter_coordinates:
                x, y, char, pressed = letter
                if pressed:
                    pygame.draw.rect(self.win, (0, 0, 0), (x, y, 30, 30), 3)
                    self.game_font.render_to(self.win, (x + 8, y + 8), char, (0, 0, 0))

            self.win.blit(self.images[Game.HANGMAN_STATUS], (150, 100))

        elif self.state == "Title":
            self.word_font.render_to(self.win, (268, 80), "HangThePyMan", (0, 0, 0), size=36)
            self.play_btn.draw(self.win)
            self.quit_btn.draw(self.win)
            self.word_font.render_to(self.win, (700, 480), "Version " + self.version, (0, 0, 0), size=15)

        elif self.state == "PostWonGame":
            self.display_message(["You won!"])
            self.end_btn.draw(self.win)
            self.replay_btn.draw(self.win)

        elif self.state == "PostLostGame":
            self.display_message(["You Lost!", f"Word was {self.word}"])
            self.end_btn.draw(self.win)
            self.replay_btn.draw(self.win)

        pygame.display.update()

    def display_message(self, message, delay=0):
        """Display message function to print out any string to screen.

        Args:
            message ([str]): The message you would like to print in list.
        """

        self.win.fill(self.b_color)
        for i in range(len(message)):
            self.word_font.render_to(self.win, (325 - i * len(message[i]) * 5, 180 + i * 50), message[i], (0, 0, 0), size=30)

    def check_collision(self, pos):
        m_x, m_y = pos
        for ltr in self.letter_coordinates:
            x, y, char, pressed = ltr
            if 0 < m_x - x < 30 and 0 < m_y - y < 30 and pressed:
                distance = (m_x - x) * (m_y - y)
                if 0 < distance <= 900:
                    ltr[3] = False
                    Game.GUESSED += char
                    Game.WON = [True if i in Game.GUESSED and self.word else False for i in self.word]
                    if char not in self.word:
                        Game.HANGMAN_STATUS += 1

    def main(self):
        while self.run:
            self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
                    self.quit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if self.state == "Game":
                        self.check_collision(pos)
                    elif self.state == "Title":
                        if self.play_btn.isOver(pos):
                            self.state = "Game"
                        elif self.quit_btn.isOver(pos):
                            self.run = False
                            self.quit()
                    elif self.state == "PostLostGame" or self.state == "PostWonGame":
                        if self.end_btn.isOver(pos):
                            self.run = False
                            self.quit()
                        elif self.replay_btn.isOver(pos):
                            Game.GUESSED = ""
                            Game.HANGMAN_STATUS = 0
                            Game.WON = [False]
                            self.letter_coordinates = self.load_buttons()
                            self.word = random_word(self.conn)[1]
                            self.state = "Game"

            self.draw()
            self.win_status(Game.WON, Game.HANGMAN_STATUS)

    def win_status(self, status, hangman_status):
        if hangman_status >= 6:
            pygame.time.delay(1000)
            self.state = "PostLostGame"

        if all(status):
            pygame.time.delay(1000)
            self.state = "PostWonGame"

    def play(self):
        self.main()

    def quit(self):
        pygame.quit()
        self.conn.close()
        sys.exit()


class Button():
    def __init__(self, color, x, y, width, height, text='', image=None, imagepos=(10, 10)):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.image = image
        if image:
            self.rect = image.get_rect(topleft=imagepos)

    def draw(self, win, outline=None):
        # Call this method to draw the button on the screen
        if self.image:
            win.blit(self.image, self.rect)
        else:
            if outline:
                pygame.draw.rect(win, outline, (self.x - 2, self.y - 2,
                                                self.width + 4, self.height + 4), 0)

            pygame.draw.rect(win, self.color, (self.x, self.y,
                                               self.width, self.height), 0)

            if self.text != '':
                font = pygame.font.SysFont('comicsans', 60)
                text = font.render(self.text, 1, (0, 0, 0))
                win.blit(text, (self.x + int(self.width / 2 - text.get_width() / 2),
                                self.y + int(self.height / 2 - text.get_height() / 2)))

    def isOver(self, pos):
        # Pos is the mouse position or a tuple of (x,y) coordinates
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True

        return False
