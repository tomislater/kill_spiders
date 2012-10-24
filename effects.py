import pygame

from tools import load_image

from settings import FPS


class Effects(pygame.sprite.Sprite):
    BLOOD_F1 = load_image('blood_f1.png')
    BLOOD_F2 = load_image('blood_f2.png')

    def __init__(self, x, y):
        super(Effects, self).__init__()

        self.images = ([self.BLOOD_F1] * (FPS / 15)) + ([self.BLOOD_F2] * (FPS / 15))
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
