import pygame
from sprites import load_sprite
class Interactable:
    def __init__(self, id, name, rect, room, verb ="Search", gives = None, found_text = "You find nothing.", empty_text = "There is nothing more here.", color = (150,60,100), solid= True, sprite=None, use=None):
        self.id = id
        self.use = use
        self.name = name
        self.rect = pygame.Rect(rect)
        self.room = room
        self.verb = verb
        self.gives = gives
        self.found_text = found_text
        self.empty_text = empty_text
        self.looted = False
        self.color = color
        self.sprite = load_sprite(sprite) if isinstance(sprite,str) else sprite
        self.solid = solid

    def distance_to(self, position):
        cx = max(self.rect.left, min(position.x, self.rect.right))
        cy = max(self.rect.top, min(position.y, self.rect.bottom))
        return pygame.Vector2(cx,cy).distance_to(position)
    def search(self,character,world=None):
        if self.use:
            return self.use(character,self,world)
        flag = "searched_" + self.id
        if self.gives:
            if self.looted:
                return self.empty_text
            self.looted = True
            character.inventory.add_item(self.gives)
            character.set_flag(flag)
            return self.found_text
        character.set_flag(flag)
        return self.found_text
    def draw(self, surface, camera):
        r = self.rect.move(-int(camera.x), -int(camera.y))
        if self.sprite:
            surface.blit(self.sprite, (r.x, r.bottom - self.sprite.get_height()))
        else:
            pygame.draw.rect(surface, self.color, r)
            pygame.draw.rect(surface, (60,40,20), r, 2)