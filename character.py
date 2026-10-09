import pygame
from inventory import Inventory

class Character:
    def __init__(self,name,  position, state):
        self.name = name
        self.position = pygame.Vector2(position)
        self.state = state
        self.speed = 170
        self.radius = 7
        self.color = (165, 0,0 )
        self.inventory = Inventory()
        self.flags = set()
        self.room = None

    def can_stand(self, position, navmesh):
        r = self.radius
        for ox,oy in ((0,0),(r,0),(-r,0),(0,r),(0,-r)):
            if not navmesh.is_walkable(pygame.Vector2(position.x+ox,position.y+oy)):
                return False
            return True

    def move(self,direction, dt, navmesh):
        if direction.length_squared() == 0:
            return
        step = direction.normalize() *self.speed *dt
        new_x = pygame.Vector2(self.position.x + step.x, self.position.y)
        if self.can_stand(new_x, navmesh):
            self.position = new_x
        new_y = pygame.Vector2(self.position.x, self.position.y+step.y)
        if self.can_stand(new_y, navmesh):
            self.position = new_y

    def draw(self, surface, camera):
        screen_position = (self.position.x - camera.x, self.position.y - camera.y)
        pygame.draw.circle(surface, self.color, (int(screen_position[0]), int(screen_position[1])), self.radius)
    def update_room(self, castle):
        self.room = castle.room_at(self.position)
    def set_flag(self,flag):
        self.flags.add(flag)
    def has_flag(self,flag):
        return flag in self.flags
    def facts(self):
        data = {"role":self.state.role.value, "room":self.room}
        for item in self.inventory.names():
            data["has_"+item]= True
        for flag in self.flags:
            data[flag]= True
        return data