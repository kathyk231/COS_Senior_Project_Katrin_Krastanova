import pygame

class Door:
    def __init__(self, name, position, allowed_role = None):
        self.name = name
        self.position = position
        self.is_open =False
        if allowed_role is None:
            self.allowed.role=[]
        else:
            self.allowed_role = allowed_role
    def can_open(self,role):
        return role in self.allowed_role
    def open_door(self):
        self.is_open = True
    def close_door(self):
        self.is_open = False