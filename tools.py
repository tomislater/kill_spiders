import os
import pygame

main_dir = os.path.split(os.path.abspath(__file__))[0]


def load_image(file):
    file = os.path.join(main_dir, 'img', file)

    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit('Could not load image "{0}" {1}'.format(file, pygame.get_error()))
    return surface.convert()


def load_sound(file):
    return os.path.join(main_dir, 'sounds', file)
