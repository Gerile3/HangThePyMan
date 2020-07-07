import os
from string import ascii_uppercase
from words import random_word
import sys
import pathlib
import pygame
import pygame.freetype
from db_connection import db_connect


class Game:
    WIDTH = 800
    HEIGHT = 500
    RADIUS = 20
    GAP = 15
    GUESSED = ""
    HANGMAN_STATUS = 0
    WON = [False]
    DIR = str(pathlib.Path(__file__).parent.absolute())

    def __init__(self):
        pygame.init()
        self.conn = db_connect(Game.DIR + "\\db\\words.db")
        self.word = random_word(self.conn)[1]
        self.game_font = pygame.freetype.Font(Game.DIR + '\\fonts\\classic.TTF', 26)
        self.word_font = pygame.freetype.SysFont("comicsans", 50)
        self.win = pygame.display.set_mode((Game.WIDTH, Game.HEIGHT))
        self.caption = pygame.display.set_caption("Hangman The Game")
        self.gameIcon = pygame.image.load(Game.DIR + '\\icon\\icon.png')
        self.icon = pygame.display.set_icon(self.gameIcon)
        self.clock = pygame.time.Clock()
        self.b_color = (255, 255, 255)
        self.run = True
        self.images = self.load_images()
        self.letter_coordinates = self.load_buttons()

    def load_images(self):
        images = []
        location = Game.DIR + "\\images"
        for i in range(len(os.listdir(location))):
            image = pygame.image.load(location + "\\" + "hangman" + str(i) + ".png")
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
        pygame.display.update()

    def display_message(self, message):
        """Display message function to print out any string to screen.

        Args:
            message ([str]): The message you would like to print
        """
        pygame.time.delay(1000)
        self.win.fill(self.b_color)
        self.word_font.render_to(self.win, (300, 180), message, (0, 0, 0))
        self.word_font.render_to(self.win, (331 - len(self.word) * 2, 280), f"Word was {self.word}", (0, 0, 0), size=20)
        pygame.display.update()
        pygame.time.delay(3000)

    def main(self):
        while self.run:
            self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
                    self.quit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    m_x, m_y = pygame.mouse.get_pos()
                    # Check collision
                    for ltr in self.letter_coordinates:
                        x, y, char, pressed = ltr
                        if 0 < m_x - x < 30 and 0 < m_y - y < 30 and pressed:
                            distance = (m_x - x) * (m_y - y)
                            if 0 < distance <= 900:
                                ltr[3] = False
                                Game.GUESSED += char
                                if char not in self.word:
                                    Game.HANGMAN_STATUS += 1

                    Game.WON = [True if i in Game.GUESSED and self.word else False for i in self.word]

            self.draw()
            result = self.win_status(Game.WON, Game.HANGMAN_STATUS)

            if result:
                self.run = False
                self.quit()

    def win_status(self, status, hangman_status):
        if hangman_status >= 6:
            self.display_message("You Lost!")
            return True

        if all(status):
            self.display_message("You won!")
            return True
        return False

    def play(self):
        self.main()

    def quit(self):
        pygame.quit()
        self.conn.close()
        sys.exit()
