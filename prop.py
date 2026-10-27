import pygame
from sprites import load_sprite
class Prop:
    def __init__(self, id, rect, room, color=(32,211,197), solid=True,sprite=None):
        self.id = id
        self.rect = pygame.Rect(rect)
        self.room = room
        self.color = color
        self.solid = solid
        self.sprite = load_sprite(sprite) if isinstance(sprite,str) else sprite
        self.sprite_offset = (0,0)

    def draw(self, surface, camera):
        r = self.rect.move(-int(camera.x), -int(camera.y))
        if self.sprite:
            surface.blit(self.sprite, (r.x + self.sprite_offset[0],r.bottom-self.sprite.get_height() + self.sprite_offset[1]))
        else:
            pygame.draw.rect(surface, self.color, r)
            pygame.draw.rect(surface, (60, 40, 20), r, 2)