import pygame

class Door:
    AUTO_CLOSE_TIMER = 3.0
    def __init__(self, name, position, allowed_role = None):
        self.name = name
        self.position = position
        self.is_open =False
        self.timer = 0.0
        self.locked = False
        if allowed_role is None:
            self.allowed_role=[]
        else:
            self.allowed_role = allowed_role
    def can_open(self,role):
        return role in self.allowed_role
    def open_door(self, role):
        if self.locked:
            return False
        if self.can_open(role):
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