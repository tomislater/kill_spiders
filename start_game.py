import random
import pygame

from pygame.locals import QUIT
from pygame.locals import K_SPACE
from pygame.locals import K_LCTRL
from pygame.locals import K_ESCAPE
from pygame.locals import KEYUP
from pygame.locals import K_y
from pygame.locals import K_n

from settings import FPS
from settings import SILVER
from settings import SCREEN_HEIGHT
from settings import SCREEN_WIDTH

pygame.init()
main_surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.mixer.init()

from tools import load_image
from tools import load_sound

from spiders import Spider
from spiders import PoisonSpider
from spiders import Tarantula
from spiders import GiantSpider
from spiders import WailingWidow

from hud import Hud
from player import Player
from effects import Effects

from weapons import WhiteSkull
from weapons import BlackSkull

__version__ = '0.1.8'


class Main(object):
    def __init__(self):
        self.MAIN_LOOP = True

        self.clock = pygame.time.Clock()
        pygame.mouse.set_visible(0)

        self.surface = main_surface
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
            spider = self.spiders[i]
            if spider.rect.top < self.deadline or (spider.rect.colliderect(self.player) and self.player.alive()):
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


if __name__ == '__main__':
    Main()
