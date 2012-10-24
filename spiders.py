import math
import random
import pygame

from tools import load_sound
from tools import load_image

from settings import FPS
from settings import SCREEN_HEIGHT
from settings import SCREEN_WIDTH


class CommonSpider(pygame.sprite.Sprite):

    hit_sound = pygame.mixer.Sound(load_sound('hit_spider.ogg'))
    hit_sound.set_volume(0.6)

    def __init__(self, img_1, img_2, img_dead, health=1):
        super(CommonSpider, self).__init__()

        self.frame_count = 0
        self.health = health
        self.score = health

        self.images = ([img_1] * (FPS / 2)) + ([img_2] * (FPS / 2))
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.bottom = SCREEN_HEIGHT + random.randint(0, SCREEN_HEIGHT / 4)
        self.rect.left = random.randint(0, SCREEN_WIDTH - self.rect.width)

        self.image_dead = img_dead
        self.rect_dead = self.image_dead.get_rect()
        self.simply_gravity = 0

    def update(self, level):
        self.image = self.images[self.frame_count % FPS]
        self.frame_count += 1
        self.rect.move_ip(0, random.randint(- int(math.log(level, 6)) - 1, 0))

    def update_dead(self):
        self.simply_gravity += 1
        self.rect_dead.move_ip(0, 2 * self.simply_gravity)

    def hit(self, hit=1):
        self.hit_sound.play()
        self.health -= hit

    def alive(self):
        if self.health > 0:
            return True
        self.get_rect_for_dead_spider()
        return False

    def get_rect_for_dead_spider(self):
        (self.rect_dead.centerx, self.rect_dead.centery) = (self.rect.centerx, self.rect.centery)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def draw_dead(self, surface):
        surface.blit(self.image_dead, self.rect_dead)


class Spider(CommonSpider):
    IMG_1 = load_image('spider_f1.png')
    IMG_2 = load_image('spider_f2.png')
    IMG_DEAD = load_image('spider_dead.png')

    def __init__(self):
        super(Spider, self).__init__(self.IMG_1, self.IMG_2, self.IMG_DEAD)


class PoisonSpider(CommonSpider):
    IMG_1 = load_image('poison_spider_f1.png')
    IMG_2 = load_image('poison_spider_f2.png')
    IMG_DEAD = load_image('poison_spider_dead.png')

    def __init__(self):
        super(PoisonSpider, self).__init__(self.IMG_1, self.IMG_2, self.IMG_DEAD, health=2)

    def update(self, level):
        self.image = self.images[self.frame_count % FPS]
        self.frame_count += 1
        self.rect.move_ip(0, random.randint(- int(math.log(level, 5)) - 1, 0))


class Tarantula(CommonSpider):
    IMG_1 = load_image('tarantula_f1.png')
    IMG_2 = load_image('tarantula_f2.png')
    IMG_DEAD = load_image('tarantula_dead.png')

    def __init__(self):
        super(Tarantula, self).__init__(self.IMG_1, self.IMG_2, self.IMG_DEAD, health=5)

    def update(self, level):
        self.image = self.images[self.frame_count % FPS]
        self.frame_count += 1
        self.rect.move_ip(0, random.randint(- int(math.log(level, 4)) - 1, 0))


class GiantSpider(CommonSpider):
    IMG_1 = load_image('giant_spider_f1.png')
    IMG_2 = load_image('giant_spider_f2.png')
    IMG_DEAD = load_image('giant_spider_dead.png')

    def __init__(self):
        super(GiantSpider, self).__init__(self.IMG_1, self.IMG_2, self.IMG_DEAD, health=15)

    def update(self, level):
        self.image = self.images[self.frame_count % FPS]
        self.frame_count += 1
        self.rect.move_ip(0, random.randint(- int(math.log(level, 3)) - 1, 0))


class WailingWidow(CommonSpider):
    IMG_1 = load_image('wailing_widow_f1.png')
    IMG_2 = load_image('wailing_widow_f2.png')
    IMG_DEAD = load_image('wailing_widow_dead.png')

    def __init__(self):
        super(WailingWidow, self).__init__(self.IMG_1, self.IMG_2, self.IMG_DEAD, health=35)

    def update(self, level):
        self.image = self.images[self.frame_count % FPS]
        self.frame_count += 1
        self.rect.move_ip(0, random.randint(- int(math.log(level, 5)) - 1, 0))
