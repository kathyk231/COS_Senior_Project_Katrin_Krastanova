import pygame
class Interactable:
    def __init__(self, id, name, rect, room):
        self.id = id
        self.name = name
        self.rect = pygame.Rect(rect)
        self.room = room
        self.color = (60,191,48)
        self.sprite = None

    def distance_to(self, position):
        cx = max(self.rect.left, min(position.x, self.rect.right))
        cy = max(self.rect.top, min(position.y, self.rect.bottom))
        return pygame.Vector2(cx,cy).distance_to(position)
    def draw(self, surface, camera):
        r = self.rect.move(-int(camera.x), int(camera.y))
        if self.sprite:
            surface.blit(self.sprite, r)
        else:
            pygame.draw.rect(surface, self.color, r)
            pygame.draw.rect(surface, (60,40,20), r, 2)