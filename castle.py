import pygame
from door import Door
from player_state import Role

class Castle:
    def __init__(self):
        self.rooms = []
        self.doors = []
        self.create_castle()
        self.create_doors()

    def create_castle(self):
        self.rooms =[
            {"name": "Great Hall",
             "rect": pygame.Rect(250, 150,460, 250)},
            {"name": "Kings Bedroom",
             "rect": pygame.Rect(500, 50, 210, 100)},
            {"name": "Treasury",
             "rect": pygame.Rect(710, 200, 150, 120)},
            {"name": "Kitchen",
             "rect": pygame.Rect(80, 200, 170, 100)}
        ]
    def create_doors(self):
        self.doors = [Door("Kitchens door",(250,270),[Role.SERVANT]),
                      Door("Treasury door",(700, 270), [Role.ROYAL]),
                      Door("Great Hall foor",(250, 270), [Role.ROYAL, Role.SERVANT]),
                      Door("Kings door",(600,150), [Role.ROYAL])]
    def draw(self, screen):
        for room in self.rooms:
            pygame.draw.rect(screen,(255,255,255),room["rect"])
            pygame.draw.rect(screen,(255, 118, 189),room["rect"],3)
        for door in self.doors:
            x,y =door.position
            if door.is_open:
                color =(0,255,0)
            else:
                color =(200,50,50)
            pygame.draw.circle(screen,color,(x,y),7)