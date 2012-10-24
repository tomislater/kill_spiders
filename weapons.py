import pygame

from tools import load_sound
from tools import load_image


class Weapon(pygame.sprite.Sprite):

    shot_sound = pygame.mixer.Sound(load_sound('shot.wav'))
    shot_sound.set_volume(0.6)

    def __init__(self, centerx, top, image, direction):
        super(Weapon, self).__init__()

        self.shot_sound.play()
        self.image = image
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
    IMG = load_image('skull.png')
    hit = 1

    def __init__(self, centerx, top, direction):
        super(WhiteSkull, self).__init__(centerx, top, self.IMG, direction)


class BlackSkull(Weapon):
    IMG = load_image('black_skull.png')
    hit = 5

    def __init__(self, centerx, top, direction):
        super(BlackSkull, self).__init__(centerx, top, self.IMG, direction)
