import pygame

from tools import load_image

from settings import SILVER
from settings import SCREEN_WIDTH


class Hud(object):
    IMG_BLACK_SKULL = load_image('black_skull.png')

    def __init__(self, font_size=20, score=0):
        self.font = pygame.font.Font(None, font_size)
        self.score = score
        self.img_black_skull = self.IMG_BLACK_SKULL

    def update_score(self, score):
        self.score += score
        if self.score < 0:
            self.score = 0

    def draw(self, surface, health, level, black_skulls):
        level = self.font.render("LEVEL: {0}".format(level), 1, SILVER)
        level_r = level.get_rect(centerx=SCREEN_WIDTH / 2, top=10)
        surface.blit(level, level_r)

        score = self.font.render("SCORE: {0}".format(self.score), 1, SILVER)
        score_r = score.get_rect(topleft=(10, 10))
        surface.blit(score, score_r)

        life = self.font.render("LIFE: ", 1, SILVER)
        life_r = score.get_rect(topleft=(10, 30))
        surface.blit(life, life_r)

        for i, img in enumerate(health):
            img_r = img.get_rect(centery=life_r.centery, left=50 + (i * 12))
            surface.blit(img, img_r)

        x = self.font.render('x {0}'.format(black_skulls), 1, SILVER)
        x_r = x.get_rect(centerx=SCREEN_WIDTH / 1.5, top=10)
        surface.blit(x, x_r)

        img_black_skull_r = self.img_black_skull.get_rect(centerx=x_r.centerx - 20, top=10)
        surface.blit(self.img_black_skull, img_black_skull_r)
