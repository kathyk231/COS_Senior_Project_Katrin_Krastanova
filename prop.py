import pygame

class Prop:
    def __init__(self, id, rect, room, color=(32,211,197), solid=True):
        self.id = id
        self.rect = pygame.Rect(rect)
        self.room = room
        self.color = color
        self.solid = solid
        self.sprite = None
        self.sprite_offset = (0,0)

    def draw(self, surface, camera):
        r = self.rect.move(-int(camera.x), -int(camera.y))
        if self.sprite:
            surface.blit(self.sprite, (r.x + self.sprite_offset[0], r.y + self.sprite_offset[1]))
        else:
            pygame.draw.rect(surface, self.color, r)
            pygame.draw.rect(surface, (60, 40, 20), r, 2)