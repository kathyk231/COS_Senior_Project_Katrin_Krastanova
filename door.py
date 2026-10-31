import pygame

class Door:
    AUTO_CLOSE_TIMER = 3.0
    def __init__(self, name, position, allowed_role = None,key=None, hidden=False):
        self.name = name
        self.position = position
        self.is_open =False
        self.timer = 0.0
        self.locked = False
        self.key = key
        self.hidden = hidden
        if allowed_role is None:
            self.allowed_role=[]
        else:
            self.allowed_role = allowed_role
    def can_open(self,character):
        if character.state.role in self.allowed_role:
            return True
        return self.key is not None and character.inventory.has(self.key)
    def open_door(self, character):
        if self.locked:
            return False
        if self.can_open(character):
            self.is_open = True
            self.timer = self.AUTO_CLOSE_TIMER
            return True
        return False
    def close_door(self):
        self.is_open = False
        self.timer = 0.0
    def update(self, dt, blocked):
        if not self.is_open:
            return
        if blocked:
            self.timer = self.AUTO_CLOSE_TIMER
            return
        self.timer -= dt
        if self.timer <= 0:
            self.close_door()