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

SILVER = (220, 220, 220)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
FPS = 30


def load_image(file):
    file = os.path.join(main_dir, 'img', file)

    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit('Could not load image "{0}" {1}'.format(file, pygame.get_error()))
    return surface.convert()


def load_sound(file):
    return os.path.join(main_dir, 'sounds', file)


pygame.init()


class Main(object):
    def __init__(self):
        self.MAIN_LOOP = True

        self.clock = pygame.time.Clock()
        pygame.mouse.set_visible(0)

        self.surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.deadline = 120  # for monster :))

        self.font = pygame.font.Font(None, 20)
        self.background = load_image('background.png')
        pygame.mixer.music.load(load_sound('background.ogg'))

        self.weapons = []
        self.spiders = []
        self.hud = Hud()
        self.level = 0

        self.level_formula = lambda x: (x + random.randint(2, x + 2)) / 2

        self.player = Player()
        self.start()

    def event(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.MAIN_LOOP = False
            elif event.type == KEYUP:
                if event.key == K_SPACE:
                    self.weapons.append(Weapon(self.player.rect.centerx, self.player.rect.centery))
                elif event.key == K_ESCAPE:
                    self.MAIN_LOOP = False

        keys = pygame.key.get_pressed()
        self.player.update(keys)

    def check_collision_spiders(self):
        for i in reversed(xrange(len(self.spiders))):
            # collision with deadline
            if self.spiders[i].rect.top < self.deadline or \
                (self.spiders[i].rect.colliderect(self.player) and self.player.alive()):
                    self.player.hit()
                    del self.spiders[i]
                    continue

    def check_collision_bone(self):
        for i in reversed(xrange(len(self.weapons))):
            # collision with spiders
            index_spider = self.weapons[i].rect.collidelist(self.spiders)
            if index_spider != -1:
                self.spiders[index_spider].hit()
                if not self.spiders[index_spider].alive():
                    self.hud.update_score(self.spiders[index_spider].score)
                    del self.spiders[index_spider]
                del self.weapons[i]
                continue

            # collison with bottom screen
            if self.weapons[i].rect.bottom > SCREEN_HEIGHT:
                del self.weapons[i]
                continue

            self.weapons[i].update()
            self.weapons[i].draw(self.surface)

    def draw_spiders(self):
        for spider in self.spiders:
            spider.update(self.level)
            spider.draw(self.surface)

    def make_spiders(self):
        lvl_formula = self.level_formula(self.level)

        for x in xrange(0, lvl_formula):
            self.spiders.append(Spider())

        for x in xrange(0, lvl_formula / 3):
            self.spiders.append(PoisonSpider())

        if self.level % 5 == 0:
            for x in xrange(0, self.level / 5):
                self.spiders.append(Tarantula())

        if self.level % 10 == 0:
            for x in xrange(0, self.level / 10):
                self.spiders.append(GiantSpider())

        if self.level % 15 == 0:
            for x in xrange(0, self.level / 15):
                self.spiders.append(Spidris())

        if self.level % 30 == 0:
            for x in xrange(0, self.level / 30):
                self.spiders.append(WailingWidow())

    def check_spiders(self):
        if not self.spiders:
            self.level += 1
            text_level = self.font.render("LEVEL {0}".format(self.level), 1, SILVER)
            text_level_p = text_level.get_rect(centerx=SCREEN_WIDTH / 2, centery=SCREEN_HEIGHT / 2)
            self.surface.blit(text_level, text_level_p)
            self.make_spiders()
            self.weapons = []
            pygame.display.update()
            self.clock.tick(FPS)
            pygame.time.delay(1500)

    def check_health(self):
        if not self.player.alive():
            game_over_text = self.font.render("GAME OVER", 1, SILVER)
            game_over_text_p = game_over_text.get_rect(centerx=SCREEN_WIDTH / 2, centery=SCREEN_HEIGHT / 2)
            self.surface.blit(game_over_text, game_over_text_p)
            pygame.display.update()
            self.clock.tick(FPS)
            self.MAIN_LOOP = False
            pygame.time.delay(2000)

    def start(self):
        pygame.mixer.music.play(-1, 0.0)
        while self.MAIN_LOOP:
            pygame.display.set_caption("Kill spiders with bones! FPS: {0:.0f}".format(self.clock.get_fps()))

            self.surface.blit(self.background, (0, 0))

            self.check_health()
            self.check_spiders()
            self.draw_spiders()

            self.player.draw(self.surface)
            self.hud.draw(self.surface, self.player.health, self.level)
            self.event()

            self.check_collision_spiders()
            self.check_collision_bone()

            pygame.display.update()
            self.clock.tick(FPS)

        pygame.mixer.music.stop()
        pygame.quit()


class CommonSpider(pygame.sprite.Sprite):

    hit_sound = pygame.mixer.Sound(load_sound('hit_spider.ogg'))
    hit_sound.set_volume(0.5)

    def __init__(self, img_1, img_2, health=1):
        super(CommonSpider, self).__init__()

        self.images = list()
        self.frame_count = 0

        self.health = health
        self.score = health

        self.images.extend([load_image(img_1)] * 15)
        self.images.extend([load_image(img_2)] * 15)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.bottom = SCREEN_HEIGHT + random.randint(0, SCREEN_HEIGHT / 4)
        self.rect.left = random.randint(0, SCREEN_WIDTH - self.rect.width)

    def update(self, level):
        self.frame_count += 1
        self.image = self.images[self.frame_count % 30]
        self.rect.move_ip(0, random.randint(- int(math.log(level, 6)) - 1, 0))

    def hit(self, hit=1):
        self.hit_sound.play()
        self.health -= hit

    def alive(self):
        if self.health:
            return True
        return False

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Spider(CommonSpider):
    IMG_1 = 'spider_f1.png'
    IMG_2 = 'spider_f2.png'

    def __init__(self):
        super(Spider, self).__init__(self.IMG_1, self.IMG_2)


class PoisonSpider(CommonSpider):
    IMG_1 = 'poison_spider_f1.png'
    IMG_2 = 'poison_spider_f2.png'

    def __init__(self):
        super(PoisonSpider, self).__init__(self.IMG_1, self.IMG_2, health=2)

    def update(self, level):
        self.frame_count += 1
        self.image = self.images[self.frame_count % 30]
        self.rect.move_ip(0, random.randint(- int(math.log(level, 5)) - 1, 0))


class Tarantula(CommonSpider):
    IMG_1 = 'tarantula_f1.png'
    IMG_2 = 'tarantula_f2.png'

    def __init__(self):
        super(Tarantula, self).__init__(self.IMG_1, self.IMG_2, health=5)

    def update(self, level):
        self.frame_count += 1
        self.image = self.images[self.frame_count % 30]
        self.rect.move_ip(0, random.randint(- int(math.log(level, 4)) - 1, 0))


class GiantSpider(CommonSpider):
    IMG_1 = 'giant_spider_f1.png'
    IMG_2 = 'giant_spider_f2.png'

    def __init__(self):
        super(GiantSpider, self).__init__(self.IMG_1, self.IMG_2, health=10)

    def update(self, level):
        self.frame_count += 1
        self.image = self.images[self.frame_count % 30]
        self.rect.move_ip(0, random.randint(- int(math.log(level, 3)) - 1, 0))


class Spidris(CommonSpider):
    IMG_1 = 'spidris_f1.png'
    IMG_2 = 'spidris_f2.png'

    def __init__(self):
        super(Spidris, self).__init__(self.IMG_1, self.IMG_2, health=15)

    def update(self, level):
        self.frame_count += 1
        self.image = self.images[self.frame_count % 30]
        self.rect.move_ip(0, random.randint(- int(math.log(level, 4)) - 2, 0))


class WailingWidow(CommonSpider):
    IMG_1 = 'wailing_widow_f1.png'
    IMG_2 = 'wailing_widow_f2.png'

    def __init__(self):
        super(WailingWidow, self).__init__(self.IMG_1, self.IMG_2, health=35)

    def update(self, level):
        self.frame_count += 1
        self.image = self.images[self.frame_count % 30]
        self.rect.move_ip(0, random.randint(- int(math.log(level, 5)) - 1, 0))


class Weapon(pygame.sprite.Sprite):

    shot_sound = pygame.mixer.Sound(load_sound('shot_bone.wav'))
    shot_sound.set_volume(0.5)

    def __init__(self, centerx, top):
        super(Weapon, self).__init__()

        self.shot_sound.play()
        self.image = load_image('bone.png')
        self.rect = self.image.get_rect()
        self.rect.top = top
        self.rect.centerx = centerx
        self.simply_gravity = 1

    def update(self):
        self.simply_gravity += 1
        self.rect.move_ip(0, 2 * self.simply_gravity)

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Player(pygame.sprite.Sprite):
    def __init__(self, health=10):
        super(Player, self).__init__()

        self.health = [load_image('life.png')] * health
        self.images_left = []
        self.images_right = []

        for i, name in enumerate(('character_left_f1.png',
                                  'character_left_f2.png',
                                  'character_left_f3.png',
                                  'character_right_f1.png',
                                  'character_right_f2.png',
                                  'character_right_f3.png',)):
            if i < 3:
                self.images_left.extend([load_image(name)] * 5)
            else:
                self.images_right.extend([load_image(name)] * 5)

        self.image = self.images_left[0]

        self.rect = self.image.get_rect()
        self.rect.top = 66
        self.rect.centerx = SCREEN_WIDTH / 2
        self.max = SCREEN_WIDTH
        self.frame_count = 1

    def update(self, keys):
        if keys[K_LEFT]:
            self.frame_count += 1
            self.image = self.images_left[self.frame_count % 15]
            self.rect.move_ip(-10, 0)
            if self.rect.centerx < 0:
                self.rect.centerx = 0
        elif keys[K_RIGHT]:
            self.frame_count += 1
            self.image = self.images_right[self.frame_count % 15]
            self.rect.move_ip(10, 0)
            if self.rect.centerx > self.max:
                self.rect.centerx = self.max

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def hit(self):
        del self.health[-1]

    def alive(self):
        if not self.health:
            return False
        return True


class Hud(object):
    def __init__(self, font_size=20, score=0):
        self.font = pygame.font.Font(None, font_size)
        self.score = score

    def update_score(self, score):
        self.score += score
        if self.score < 0:
            self.score = 0

    def draw(self, surface, health, level):
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


if __name__ == '__main__':
    Main()
