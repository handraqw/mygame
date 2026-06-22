import pygame
import os


def load_and_scale(path, target_size=None, alpha=True):
    try:
        img = pygame.image.load(path)
        img = img.convert_alpha() if alpha else img.convert()
        if target_size:
            img = pygame.transform.smoothscale(img, target_size)
        return img
    except Exception:
        return None


def first_png_in(dirpath):
    try:
        for fn in os.listdir(dirpath):
            if fn.lower().endswith('.png'):
                return os.path.join(dirpath, fn)
    except Exception:
        return None
    return None