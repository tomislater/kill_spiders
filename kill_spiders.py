import os
import random
import math
import pygame

from pygame.locals import QUIT
from pygame.locals import K_LEFT
from pygame.locals import K_RIGHT
from pygame.locals import K_SPACE
from pygame.locals import K_ESCAPE
from pygame.locals import KEYUP

main_dir = os.path.split(os.path.abspath(__file__))[0]


def load_image(file):
    file = os.path.join(main_dir, 'img', file)

    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit('Could not load image "{0}" {1}'.format(file, pygame.get_error()))
    return surface.convert()


class Main(object):

    BLACK = (0, 0, 0)
    GREEN = (0, 200, 0)
    RED = (200, 0, 0)
    SILVER = (200, 200, 200)
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 800
    FPS = 30
    RATIO_FONT = 0.05

    def __init__(self):
        self.MAIN_LOOP = True

        pygame.init()
        pygame.mouse.set_visible(0)
        self.clock = pygame.time.Clock()
        self.surface = pygame.display.set_mode((self.SCREEN_WIDTH,
                                                self.SCREEN_HEIGHT))

        self.font = pygame.font.Font(None, int(self.SCREEN_HEIGHT * self.RATIO_FONT))
        self.distance_hud = int(self.RATIO_FONT * 250)  # distance for font

        self.bags = []
        self.spiders = []
        self.score = 0
        self.level = 0
        self.health = 30
        self.health_width = self.SCREEN_WIDTH / 4
        self.health_ratio = self.health_width / float(self.health)

        self.level_formula = lambda x: (2 * x + random.randint(1, x + 1)) / 3

        self.player = Player(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)

        self.start()

    def event(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.MAIN_LOOP = False
            elif event.type == KEYUP:
                if event.key == K_SPACE:
                    self.bags.append(Bag(self.player.rect.centerx, self.player.rect.centery))
                elif event.key == K_ESCAPE:
                    self.MAIN_LOOP = False

        keys = pygame.key.get_pressed()

        self.player.update(keys)

    def check_collision_spiders(self):
        for i in reversed(xrange(len(self.spiders))):
            # collision with hud
            if self.spiders[i].rect.centery < self.distance_hud * 2 or \
                self.spiders[i].rect.colliderect(self.player):
                self.health -= self.spiders[i].health
                self.score -= self.spiders[i].score
                self.health_width -= self.health_ratio
                del self.spiders[i]
                continue

    def check_collision_bag(self):
        for i in reversed(xrange(len(self.bags))):
            # collison with bottom screen
            if self.bags[i].rect.bottom > self.SCREEN_HEIGHT:
                del self.bags[i]
                self.score -= 2
                continue

            # collision with spiders
            index_spider = self.bags[i].rect.collidelist(self.spiders)
            if index_spider != -1:
                self.spiders[index_spider].hit()
                if not self.spiders[index_spider].alive():
                    self.score += self.spiders[index_spider].score
                    del self.spiders[index_spider]
                del self.bags[i]
                continue

            self.bags[i].update()
            self.surface.blit(self.bags[i].image, self.bags[i].rect)

    def draw_spiders(self):
        for spider in self.spiders:
            spider.update(self.level)
            self.surface.blit(spider.image, spider.rect)

    def make_spiders(self):
        lvl_formula = self.level_formula(self.level)
        w, h = self.SCREEN_WIDTH, self.SCREEN_HEIGHT

        for x in xrange(0, lvl_formula):
            self.spiders.append(Spider(w, h))

        for x in xrange(0, lvl_formula / 3):
            self.spiders.append(PoisonSpider(w, h))

        if self.level % 5 == 0:
            for x in xrange(0, self.level / 5):
                self.spiders.append(GiantSpider(w, h))

        if self.level % 10 == 0:
            for x in xrange(0, self.level / 10):
                self.spiders.append(CrystalSpider(w, h))

    def draw_player(self):
        self.surface.blit(self.player.image, self.player.rect)

    def draw_hud(self):
        hud = pygame.Surface((self.SCREEN_WIDTH, self.distance_hud * 2))
        hud.fill(self.GREEN)
        hud_p = hud.get_rect()

        score = self.font.render("SCORE: {0}".format(self.score), 1, self.SILVER)
        score_p = score.get_rect(left=self.distance_hud, centery=self.distance_hud)

        level = self.font.render("LEVEL: {0}".format(self.level), 1, self.SILVER)
        level_p = score.get_rect(right=self.SCREEN_WIDTH - self.distance_hud, centery=self.distance_hud)

        hp_text = self.font.render("HP: {0}".format(self.health), 1, self.SILVER)
        hp_text_p = hp_text.get_rect(centerx=self.SCREEN_WIDTH / 2, centery=self.distance_hud)

        if self.health_width >= 0:
            hp = pygame.Surface((self.health_width, 30))
            hp.fill(self.RED)
            hp_p = hp.get_rect(centerx=self.SCREEN_WIDTH / 2, centery=self.distance_hud)
            hud.blit(hp, hp_p)

        hud.blit(score, score_p)
        hud.blit(level, level_p)
        hud.blit(hp_text, hp_text_p)
        self.surface.blit(hud, hud_p)

    def check_spiders(self):
        if not self.spiders:
            self.level += 1
            text_level = self.font.render("LEVEL {0}".format(self.level), 1, self.SILVER)
            text_level_p = text_level.get_rect(centerx=self.SCREEN_WIDTH / 2, centery=self.SCREEN_HEIGHT / 2)
            self.surface.blit(text_level, text_level_p)
            self.make_spiders()
            self.bags = []
            pygame.display.update()
            pygame.time.delay(1000)

    def check_health(self):
        if self.health <= 0:
            game_over_text = self.font.render("GAME OVER", 1, self.SILVER)
            game_over_text_p = game_over_text.get_rect(centerx=self.SCREEN_WIDTH / 2, centery=self.SCREEN_HEIGHT / 2)
            self.surface.blit(game_over_text, game_over_text_p)
            pygame.display.update()
            self.MAIN_LOOP = False
            pygame.time.delay(2000)

    def start(self):
        while self.MAIN_LOOP:
            pygame.display.set_caption("Kill spiders with bags! FPS: {0:.0f}".format(self.clock.get_fps()))

            self.surface.fill(self.BLACK)

            self.check_health()
            self.check_spiders()
            self.draw_spiders()

            self.draw_player()
            self.draw_hud()
            self.event()

            self.check_collision_spiders()
            self.check_collision_bag()

            pygame.display.update()
            self.clock.tick(self.FPS)

        pygame.quit()


class CommonSpider(pygame.sprite.Sprite):
    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT, img_1, img_2, health=1, score=1):
        super(CommonSpider, self).__init__()

        self.images = list()
        self.frame_count = 0

        self.health = health
        self.score = score

        self.images.extend([load_image(img_1)] * 15)
        self.images.extend([load_image(img_2)] * 15)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.bottom = SCREEN_HEIGHT + random.randint(0, SCREEN_HEIGHT / 4)
        self.rect.left = random.randint(0, SCREEN_WIDTH - self.rect.width)

    def update(self, level):
        self.frame_count += 1
        self.image = self.images[self.frame_count % len(self.images)]
        self.rect.move_ip(0, random.randint(- int(math.log(level, 5)) - 1, 0))

    def hit(self):
        self.health -= 1

    def alive(self):
        if self.health:
            return True
        return False


class Spider(CommonSpider):
    IMG_1 = 'spider_f1.png'
    IMG_2 = 'spider_f2.png'

    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT):
        super(Spider, self).__init__(SCREEN_WIDTH, SCREEN_HEIGHT, self.IMG_1, self.IMG_2)


class PoisonSpider(CommonSpider):
    IMG_1 = 'poison_spider_f1.png'
    IMG_2 = 'poison_spider_f2.png'

    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT):
        super(PoisonSpider, self).__init__(SCREEN_WIDTH, SCREEN_HEIGHT, self.IMG_1, self.IMG_2, health=2, score=2)

    def update(self, level):
        self.frame_count += 1
        self.image = self.images[self.frame_count % len(self.images)]
        self.rect.move_ip(0, random.randint(- int(math.log(level, 4)) - 1, 0))


class GiantSpider(CommonSpider):
    IMG_1 = 'giant_spider_f1.png'
    IMG_2 = 'giant_spider_f2.png'

    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT):
        super(GiantSpider, self).__init__(SCREEN_WIDTH, SCREEN_HEIGHT, self.IMG_1, self.IMG_2, health=5, score=5)

    def update(self, level):
        self.frame_count += 1
        self.image = self.images[self.frame_count % len(self.images)]
        self.rect.move_ip(0, random.randint(- int(math.log(level, 3)) - 1, 0))


class CrystalSpider(CommonSpider):
    IMG_1 = 'crystal_spider_f1.png'
    IMG_2 = 'crystal_spider_f2.png'

    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT):
        super(CrystalSpider, self).__init__(SCREEN_WIDTH, SCREEN_HEIGHT, self.IMG_1, self.IMG_2, health=10, score=10)

    def update(self, level):
        self.frame_count += 1
        self.image = self.images[self.frame_count % len(self.images)]
        self.rect.move_ip(0, random.randint(- int(math.log(level, 3)) - 1, 0))


class Bag(pygame.sprite.Sprite):
    def __init__(self, centerx, top):
        super(Bag, self).__init__()

        self.image = load_image('bag.gif')
        self.rect = self.image.get_rect()
        self.rect.top = top
        self.rect.centerx = centerx
        self.simply_gravity = 1

    def update(self):
        self.simply_gravity += 1
        self.rect.move_ip(0, 2 * self.simply_gravity)


class Player(pygame.sprite.Sprite):
    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT):
        super(Player, self).__init__()

        self.image = load_image('baba.png')
        self.rect = self.image.get_rect()
        self.rect.top = SCREEN_HEIGHT / 15
        self.rect.centerx = (SCREEN_WIDTH / 2)
        self.max = SCREEN_WIDTH

    def update(self, keys):
        if keys[K_LEFT]:
            self.rect.move_ip(-15, 0)
            if self.rect.centerx < 0:
                self.rect.centerx = 0
        elif keys[K_RIGHT]:
            self.rect.move_ip(15, 0)
            if self.rect.centerx > self.max:
                self.rect.centerx = self.max


if __name__ == '__main__':
    Main()
