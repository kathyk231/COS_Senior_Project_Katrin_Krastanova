import os
import pygame

SCALE=4
BASE = os.path.dirname(os.path.abspath(__file__))
_cache ={}
def load_image(folder, name, scale=SCALE):
    key = (folder, name,scale)
    if key in _cache:
        return _cache[key]
    path = os.path.join(BASE, "assets", folder, name + ".png")
    img = None
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        if scale != 1:
            img = pygame.transform.scale(img, (int(img.get_width()*scale), int(img.get_height()*scale)))
    _cache[key] = img
    return img
def load_sprite(name):
    return load_image("furniture", name)