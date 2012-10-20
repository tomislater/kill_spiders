import os
import random
import math
import pygame

from pygame.locals import QUIT
from pygame.locals import K_LEFT
from pygame.locals import K_RIGHT
from pygame.locals import K_SPACE
from pygame.locals import K_LCTRL
from pygame.locals import K_ESCAPE
from pygame.locals import KEYUP
from pygame.locals import K_y
from pygame.locals import K_n

__version__ = '0.1.7'

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

        self.font = pygame.font.Font(None, 30)
        self.background = load_image('background.png')
        pygame.mixer.music.load(load_sound('background.ogg'))

        self.brushing()

        self.level_formula = lambda x: (x + random.randint(5, x + 5))
        self.start()

    def brushing(self):
        self.weapons = []
        self.spiders = []
        self.effects = []
        self.dead_spiders = []
        self.hud = Hud()
        self.player = Player()
        self.level = 0

    def event(self):
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                self.MAIN_LOOP = False
            elif event.type == KEYUP:
                if event.key == K_LCTRL:
                    self.weapons.append(WhiteSkull(self.player.rect.centerx, self.player.rect.centery, self.player.direction))
                elif event.key == K_SPACE:
                    if self.player.black_skulls:
                        self.weapons.append(BlackSkull(self.player.rect.centerx, self.player.rect.centery, self.player.direction))
                        self.player.black_skulls -= 1

        keys = pygame.key.get_pressed()
        self.player.update(keys)

    def check_collision_spiders(self):
        for i in reversed(xrange(len(self.spiders))):
            # collision with deadline and player
            if self.spiders[i].rect.top < self.deadline or \
                (self.spiders[i].rect.colliderect(self.player) and self.player.alive()):
                    self.player.hit()
                    self.spiders[i].get_rect_for_dead_spider()
                    self.dead_spiders.append(self.spiders.pop(i))
                    continue

        for i in reversed(xrange(len(self.dead_spiders))):
            # collision with bottom screen
            if self.dead_spiders[i].rect_dead.top > SCREEN_HEIGHT:
                del self.dead_spiders[i]
                continue

    def check_collision_weapons(self):
        for i in reversed(xrange(len(self.weapons))):
            # collision with spiders
            index_spider = self.weapons[i].rect.collidelist(self.spiders)
            if index_spider != -1:
                (x, y) = self.spiders[index_spider].rect.centerx, self.spiders[index_spider].rect.centery
                self.effects.append(Effects(x, y))
                self.spiders[index_spider].hit(self.weapons[i].hit)
                if not self.spiders[index_spider].alive():
                    self.hud.update_score(self.spiders[index_spider].score)
                    self.dead_spiders.append(self.spiders.pop(index_spider))
                del self.weapons[i]
                continue

            # collison with bottom screen
            if self.weapons[i].rect.bottom > SCREEN_HEIGHT:
                del self.weapons[i]
                continue

            self.weapons[i].update()
            self.weapons[i].draw(self.surface)

    def draw_effects(self):
        for i in reversed(xrange(len(self.effects))):
            if self.effects[i].alive():
                self.effects[i].update()
                self.effects[i].draw(self.surface)
            else:
                del self.effects[i]

    def draw_spiders(self):
        for spider in self.spiders:
            spider.update(self.level)
            spider.draw(self.surface)

    def draw_dead_spiders(self):
        for dead_spider in self.dead_spiders:
            dead_spider.update_dead()
            dead_spider.draw_dead(self.surface)

    def make_spiders(self):
        lvl_formula = self.level_formula(self.level)

        for x in xrange(0, lvl_formula):
            self.spiders.append(Spider())

        for x in xrange(0, lvl_formula / 3):
            self.spiders.append(PoisonSpider())

        if self.level > 5:
            for x in xrange(0, self.level / 5):
                self.spiders.append(Tarantula())

        if self.level % 10 == 0:
            for x in xrange(0, self.level / 10):
                self.spiders.append(GiantSpider())

        if self.level % 15 == 0:
            for x in xrange(0, self.level / 30):
                self.spiders.append(WailingWidow())

    def check_spiders(self):
        if not self.spiders:
            self.player.black_skulls += 1
            self.level += 1

            text_level = self.font.render("LEVEL {0}".format(self.level), True, SILVER)
            text_level_r = text_level.get_rect(centerx=SCREEN_WIDTH / 2, centery=SCREEN_HEIGHT / 2)

            self.surface.blit(self.background, (0, 0))
            self.surface.blit(text_level, text_level_r)

            self.player.draw(self.surface)
            self.hud.draw(self.surface, self.player.health, self.level, self.player.black_skulls)

            self.make_spiders()
            self.weapons = []
            self.effects = []
            self.dead_spiders = []
            pygame.display.update()
            self.clock.tick(FPS)
            pygame.time.delay(1500)

    def check_health(self):
        if not self.player.alive():
            self.animation_game_over()

    def animation_game_over(self):
        game_over_text = self.font.render("GAME OVER", 1, SILVER)
        game_over_text_r = game_over_text.get_rect(centerx=SCREEN_WIDTH / 2, centery=SCREEN_HEIGHT / 2)

        self.surface.blit(self.background, (0, 0))
        self.surface.blit(game_over_text, game_over_text_r)
        self.player.draw(self.surface)
        self.hud.draw(self.surface, self.player.health, self.level, self.player.black_skulls)

        pygame.display.update()
        self.clock.tick(FPS)
        pygame.time.delay(1000)

        self.prompt_to_game()

    def prompt_to_game(self):
        prompt_text = self.font.render("Play again? [y / n]", 1, SILVER)
        prompt_text_r = prompt_text.get_rect(centerx=SCREEN_WIDTH / 2, centery=SCREEN_HEIGHT / 2)
        prompt_loop = True

        while prompt_loop:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.MAIN_LOOP = False
                    prompt_loop = False
                elif event.type == KEYUP:
                    if event.key in (K_ESCAPE, K_n):
                        self.MAIN_LOOP = False
                        prompt_loop = False
                    elif event.key == K_y:
                        self.brushing()
                        prompt_loop = False

            self.surface.blit(self.background, (0, 0))
            self.player.draw(self.surface)
            self.hud.draw(self.surface, self.player.health, self.level, self.player.black_skulls)
            self.surface.blit(prompt_text, prompt_text_r)

            pygame.display.update()
            self.clock.tick(FPS)

    def start(self):
        pygame.mixer.music.play(-1, 0.0)

        text_controls_ctrl = self.font.render("CTRL - White Skulls (Power: 1)", True, SILVER)
        text_controls_space = self.font.render("SPACE - Black Skulls (Power: 5)", True, SILVER)
        text_info = self.font.render("ONE BLACK SKULL FOR NEXT LEVEL", True, SILVER)
        text_controls_ctrl_r = text_controls_ctrl.get_rect(centerx=SCREEN_WIDTH / 2,
                                                           centery=(SCREEN_HEIGHT / 2) + 30)
        text_controls_space_r = text_controls_space.get_rect(centerx=text_controls_ctrl_r.centerx,
                                                             centery=text_controls_ctrl_r.centery + 30)
        text_info_r = text_info.get_rect(centerx=text_controls_space_r.centerx,
                                         centery=text_controls_space_r.centery + 60)
        self.surface.blit(text_controls_ctrl, text_controls_ctrl_r)
        self.surface.blit(text_controls_space, text_controls_space_r)
        self.surface.blit(text_info, text_info_r)
        pygame.display.update()
        self.clock.tick(FPS)
        pygame.time.delay(3000)

        while self.MAIN_LOOP:
            pygame.display.set_caption("Kill spiders with bones! FPS: {0:.0f}".format(self.clock.get_fps()))

            self.surface.blit(self.background, (0, 0))

            self.draw_dead_spiders()

            self.check_spiders()
            self.draw_spiders()

            self.player.draw(self.surface)
            self.hud.draw(self.surface, self.player.health, self.level, self.player.black_skulls)
            self.event()

            self.check_collision_spiders()
            self.check_collision_weapons()

            self.check_health()

            self.draw_effects()

            pygame.display.update()
            self.clock.tick(FPS)

        pygame.mixer.music.stop()
        pygame.quit()


class CommonSpider(pygame.sprite.Sprite):

    hit_sound = pygame.mixer.Sound(load_sound('hit_spider.ogg'))
    hit_sound.set_volume(0.6)

    def __init__(self, img_1, img_2, img_dead, health=1):
        super(CommonSpider, self).__init__()

        self.images = list()
        self.frame_count = 0

        self.health = health
        self.score = health

        self.images.extend([load_image(img_1)] * (FPS / 2))
        self.images.extend([load_image(img_2)] * (FPS / 2))
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.bottom = SCREEN_HEIGHT + random.randint(0, SCREEN_HEIGHT / 4)
        self.rect.left = random.randint(0, SCREEN_WIDTH - self.rect.width)

        self.image_dead = load_image(img_dead)
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
    IMG_1 = 'spider_f1.png'
    IMG_2 = 'spider_f2.png'
    IMG_DEAD = 'spider_dead.png'

    def __init__(self):
        super(Spider, self).__init__(self.IMG_1, self.IMG_2, self.IMG_DEAD)


class PoisonSpider(CommonSpider):
    IMG_1 = 'poison_spider_f1.png'
    IMG_2 = 'poison_spider_f2.png'
    IMG_DEAD = 'poison_spider_dead.png'

    def __init__(self):
        super(PoisonSpider, self).__init__(self.IMG_1, self.IMG_2, self.IMG_DEAD, health=2)

    def update(self, level):
        self.image = self.images[self.frame_count % FPS]
        self.frame_count += 1
        self.rect.move_ip(0, random.randint(- int(math.log(level, 5)) - 1, 0))


class Tarantula(CommonSpider):
    IMG_1 = 'tarantula_f1.png'
    IMG_2 = 'tarantula_f2.png'
    IMG_DEAD = 'tarantula_dead.png'

    def __init__(self):
        super(Tarantula, self).__init__(self.IMG_1, self.IMG_2, self.IMG_DEAD, health=5)

    def update(self, level):
        self.image = self.images[self.frame_count % FPS]
        self.frame_count += 1
        self.rect.move_ip(0, random.randint(- int(math.log(level, 4)) - 1, 0))


class GiantSpider(CommonSpider):
    IMG_1 = 'giant_spider_f1.png'
    IMG_2 = 'giant_spider_f2.png'
    IMG_DEAD = 'giant_spider_dead.png'

    def __init__(self):
        super(GiantSpider, self).__init__(self.IMG_1, self.IMG_2, self.IMG_DEAD, health=15)

    def update(self, level):
        self.image = self.images[self.frame_count % FPS]
        self.frame_count += 1
        self.rect.move_ip(0, random.randint(- int(math.log(level, 3)) - 1, 0))


class WailingWidow(CommonSpider):
    IMG_1 = 'wailing_widow_f1.png'
    IMG_2 = 'wailing_widow_f2.png'
    IMG_DEAD = 'wailing_widow_dead.png'

    def __init__(self):
        super(WailingWidow, self).__init__(self.IMG_1, self.IMG_2, self.IMG_DEAD, health=35)

    def update(self, level):
        self.image = self.images[self.frame_count % FPS]
        self.frame_count += 1
        self.rect.move_ip(0, random.randint(- int(math.log(level, 5)) - 1, 0))


class Effects(pygame.sprite.Sprite):
    BLOOD_F1 = 'blood_f1.png'
    BLOOD_F2 = 'blood_f2.png'

    def __init__(self, x, y):
        super(Effects, self).__init__()

        self.images = ([load_image(self.BLOOD_F1)] * (FPS / 15)) + ([load_image(self.BLOOD_F2)] * (FPS / 15))
        self.rect = self.images[0].get_rect(centerx=x, centery=y)
        self.frame_count = 0
        self.simply_gravity = 0

    def update(self):
        self.simply_gravity += 1
        self.image = self.images[self.frame_count % len(self.images)]
        self.frame_count += 1
        self.rect.move_ip(0, self.simply_gravity)

    def alive(self):  # ;))
        if self.frame_count > len(self.images):
            return False
        return True

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Weapon(pygame.sprite.Sprite):

    shot_sound = pygame.mixer.Sound(load_sound('shot.wav'))
    shot_sound.set_volume(0.6)

    def __init__(self, centerx, top, image, direction):
        super(Weapon, self).__init__()

        self.shot_sound.play()
        self.image = load_image(image)
        self.rect = self.image.get_rect()
        self.rect.top = top
        self.rect.centerx = centerx
        self.simply_gravity = 1
        self.direction = direction

    def update(self):
        self.simply_gravity += 1
        self.rect.move_ip(self.direction, 2 * self.simply_gravity)

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class WhiteSkull(Weapon):
    IMG = 'skull.png'
    hit = 1

    def __init__(self, centerx, top, direction):
        super(WhiteSkull, self).__init__(centerx, top, self.IMG, direction)


class BlackSkull(Weapon):
    IMG = 'black_skull.png'
    hit = 5

    def __init__(self, centerx, top, direction):
        super(BlackSkull, self).__init__(centerx, top, self.IMG, direction)


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
                self.images_left.extend([load_image(name)] * (FPS / 6))
            else:
                self.images_right.extend([load_image(name)] * (FPS / 6))

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


class Hud(object):
    def __init__(self, font_size=20, score=0):
        self.font = pygame.font.Font(None, font_size)
        self.score = score
        self.img_black_skull = load_image('black_skull.png')

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


if __name__ == '__main__':
    Main()
