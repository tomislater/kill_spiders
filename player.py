import pygame

from pygame.locals import K_LEFT
from pygame.locals import K_RIGHT

from tools import load_image

from settings import FPS
from settings import SCREEN_WIDTH


class Player(pygame.sprite.Sprite):
    IMG_HEALTH = load_image('life.png')

    CHAR_LEFT_F1 = load_image('character_left_f1.png')
    CHAR_LEFT_F2 = load_image('character_left_f2.png')
    CHAR_LEFT_F3 = load_image('character_left_f3.png')

    CHAR_RIGHT_F1 = load_image('character_right_f1.png')
    CHAR_RIGHT_F2 = load_image('character_right_f2.png')
    CHAR_RIGHT_F3 = load_image('character_right_f3.png')

    def __init__(self, health=10):
        super(Player, self).__init__()

        self.health = [self.IMG_HEALTH] * health
        self.images_left = []
        self.images_right = []

        for i, name in enumerate((self.CHAR_LEFT_F1,
                                  self.CHAR_LEFT_F2,
                                  self.CHAR_LEFT_F3,
                                  self.CHAR_RIGHT_F1,
                                  self.CHAR_RIGHT_F2,
                                  self.CHAR_RIGHT_F3,)):
            if i < 3:
                self.images_left.extend([name] * (FPS / 6))
            else:
                self.images_right.extend([name] * (FPS / 6))

        self.image = self.images_left[0]

        self.rect = self.image.get_rect()
        self.rect.top = 66
        self.rect.centerx = SCREEN_WIDTH / 2
        self.max = SCREEN_WIDTH
        self.frame_count = 1

        self.black_skulls = 0

        # for left
        self.direction = -10

    def update(self, keys):
        if keys[K_LEFT]:
            self.direction = -10
            self.frame_count += 1
            self.image = self.images_left[self.frame_count % (FPS / 2)]
            self.rect.move_ip(-10, 0)
            if self.rect.centerx < 0:
                self.rect.centerx = 0
        elif keys[K_RIGHT]:
            self.direction = 10
            self.frame_count += 1
            self.image = self.images_right[self.frame_count % (FPS / 2)]
            self.rect.move_ip(10, 0)
            if self.rect.centerx > self.max:
                self.rect.centerx = self.max

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def hit(self):
        if self.health:
            del self.health[-1]

    def alive(self):
        if not self.health:
            return False
        return True
