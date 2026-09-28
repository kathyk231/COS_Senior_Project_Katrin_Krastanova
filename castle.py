import pygame


class Castle:
    def __init__(self):
        self.rooms = []
        self.create_castle()

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
    def draw(self, screen):
        for room in self.rooms:
            pygame.draw.rect(screen,(255,255,255),room["rect"])
            pygame.draw.rect(screen,(255, 118, 189),room["rect"],3)