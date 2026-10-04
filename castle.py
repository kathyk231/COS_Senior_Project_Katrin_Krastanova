import pygame
from door import Door
from player_state import Role

class Castle:
    def __init__(self):
        self.width = 1800
        self.height = 1200
        self.rooms = []
        self.doors = []
        self.create_castle()
        self.create_doors()

    def create_castle(self):
        self.rooms =[
            {"name": "Great Hall/Throne Room",
             "rect": pygame.Rect(500, 200,450, 300)},
            {"name": "Kings Bedroom",
             "rect": pygame.Rect(1050, 650, 300, 250)},
            {"name": "Servants Quarters",
             "rect": pygame.Rect(150, 450, 300, 220)},
            {"name": "Kitchen",
             "rect": pygame.Rect(150, 200, 250, 180)},
            {"name": "Quueens Room",
             "rect": pygame.Rect(1050, 400, 300, 200)},
            {"name": "Royal Room",
             "rect": pygame.Rect(1050, 150, 300, 200)},
            {"name": "Back Garden",
             "rect": pygame.Rect(100, 750, 500, 300)},
            {"name": "Stable",
             "rect": pygame.Rect(650,850, 350, 220)},
            {"name": "Woods",
             "rect": pygame.Rect(1100, 900, 400, 250)},
            {"name": "Witch House",
             "rect": pygame.Rect(1500, 850, 250, 200)}
        ]
    def create_doors(self):
        self.doors = [Door("Kitchens door",(400,290),[Role.SERVANT, Role.ROYAL]),
                      Door("Throne Room door",(500, 350), [Role.ROYAL, Role.SERVANT]),
                      Door("Royal Room door",(1050, 250), [Role.ROYAL]),
                      Door("Kings door",(1050,775), [Role.ROYAL]),
                      Door("Queens Room door",(1500, 500), [Role.ROYAL]),
                      Door("Servants Room door", (450, 550), [Role.SERVANT]),
                      Door("Stable door", (825, 850), [Role.ROYAL, Role.SERVANT]),
                      Door("Garden door", (300, 750), [Role.ROYAL, Role.SERVANT]),
                      Door("Woods entrance", (1100, 1025), [Role.ROYAL, Role.SERVANT]),
                      Door("Witch house door", (1500, 950), [Role.ROYAL, Role.SERVANT]),
                      Door("Hidden passage - KR", (1200, 900), [Role.ROYAL, Role.SERVANT]),
                      Door("Hidden passage - SB", (850, 850), [Role.ROYAL, Role.SERVANT])

                      ]
    def draw(self, screen, camera):
        for room in self.rooms:
            rect = room["rect"].move(-int(camera.x), -int(camera.y))
            pygame.draw.rect(screen,(230,230,230),rect)
            pygame.draw.rect(screen,(255, 118, 189),rect,3)
        for door in self.doors:
            x = door.position[0] - camera.x
            y = door.position[1] - camera.y
            if door.is_open:
                color =(0,255,0)
            else:
                color =(0,50,255)
            pygame.draw.circle(screen,color,(int(x),int(y)),7)