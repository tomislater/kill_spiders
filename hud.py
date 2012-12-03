import pickle
import pygame

from tools import os
from tools import load_image

from settings import SILVER
from settings import SCREEN_WIDTH

main_dir = os.path.split(os.path.abspath(__file__))[0]


class Hud(object):
    IMG_BLACK_SKULL = load_image('black_skull.png')
    HIGHSCORE_FILE = os.path.join(main_dir, 'highscore.dat')

    def __init__(self, font_size=24, score=0):
        self.font = pygame.font.Font(None, font_size)
        self.img_black_skull = self.IMG_BLACK_SKULL

        self.score = score
        try:
            with open(self.HIGHSCORE_FILE, 'rb') as f:
                self.highscore = pickle.load(f)
        except IOError:
            self.highscore = 0
            with open(self.HIGHSCORE_FILE, 'wb') as f:
                pickle.dump(self.highscore, f)

    def update_score(self, score):
        self.score += score
        if self.score < 0:
            self.score = 0

        if self.score > self.highscore:
            self.highscore = self.score

    def save_highscore(self):
        with open(self.HIGHSCORE_FILE, 'wb') as f:
            pickle.dump(self.highscore, f)

    def draw(self, surface, health, level, black_skulls, time, bonus_time, timmer):
        level = self.font.render("LEVEL: {0}".format(level), 1, SILVER)
        level_r = level.get_rect(centerx=SCREEN_WIDTH / 2, top=10)
        surface.blit(level, level_r)

        score = self.font.render("SCORE: {0}".format(self.score), 1, SILVER)
        score_r = score.get_rect(topleft=(10, 10))
        surface.blit(score, score_r)

        hscore = self.font.render("HIGHSCORE: {0}".format(self.highscore), 1, SILVER)
        hscore_r = hscore.get_rect(topleft=(10, 30))
        surface.blit(hscore, hscore_r)

        life = self.font.render("LIFE: ", 1, SILVER)
        life_r = score.get_rect(topleft=(10, 50))
        surface.blit(life, life_r)

        for i, img in enumerate(health):
            img_r = img.get_rect(centery=life_r.centery, left=55 + (i * 12))
            surface.blit(img, img_r)

        img_black_skull_r = self.img_black_skull.get_rect(centerx=SCREEN_WIDTH / 1.5, top=10)
        surface.blit(self.img_black_skull, img_black_skull_r)

        x = self.font.render('x {0}'.format(black_skulls), 1, SILVER)
        x_r = x.get_rect(topleft=(img_black_skull_r.centerx + 15, 10))
        surface.blit(x, x_r)

        if bonus_time:
            bonus = self.font.render('BONUS TIME: {0:.0f}'.format(timmer - (time.time() - bonus_time)), True, SILVER)
        else:
            bonus = self.font.render('BONUS TIME: 0', True, SILVER)
        bonus_r = bonus.get_rect(topleft=(10, 70))
        surface.blit(bonus, bonus_r)
