import pygame
from door import Door
from player_state import Role

class Castle:
    def __init__(self):
        self.width = 2604
        self.height = 2000
        self.rooms = []
        self.doors = []
        self.passage =[pygame.Rect(1712, 992, 96, 464)]
        self.create_castle()
        self.create_doors()

    def create_castle(self):
        self.rooms =[
            {"name": "Great Hall/Throne Room",
             "rect": pygame.Rect(588, 328,960, 664)},
            {"name": "Kings Bedroom",
             "rect": pygame.Rect(1548, 328, 432, 664)},
            {"name": "Corridor",
             "rect": pygame.Rect(0, 564, 588, 136)},
            {"name": "Kitchen",
             "rect": pygame.Rect(0, 1272, 588, 500)},
            {"name": "Queens Room",
             "rect": pygame.Rect(0, 700, 588, 572)},
            {"name": "Royal Room",
             "rect": pygame.Rect(0, 4, 588, 560)},
            {"name": "Stable",
             "rect": pygame.Rect(1548,1456, 432, 544)},
            {"name": "Woods",
             "rect": pygame.Rect(1980, 0, 624, 2000)},
            {"name": "Entrance Hall",
             "rect": pygame.Rect(588, 992, 960, 1008)},
            {"name": "Witch House",
             "rect": pygame.Rect(2088, 0, 516, 480)}
        ]
    def create_doors(self):
        self.doors = [Door("Kitchens door",(588,1448),[Role.SERVANT]),
                      Door("Throne Room door",(1068, 992), [Role.ROYAL, Role.SERVANT]),
                      Door("Royal Room door",(296, 564), [Role.ROYAL]),
                      Door("Kings door",(1548,660), [Role.ROYAL]),
                      Door("Queens Room door",(296, 700), [Role.ROYAL]),
                      Door("Entrance hall main door", (1068, 2000), [Role.SERVANT, Role.ROYAL]),
                      Door("Stable door", (1548, 1728), [Role.ROYAL, Role.SERVANT]),
                      Door("Corridor door", (588, 632), [Role.ROYAL, Role.SERVANT]),
                      Door("Woods entrance", (1980, 1872), [Role.ROYAL, Role.SERVANT]),
                      Door("Witch house door", (2344, 480), [Role.ROYAL, Role.SERVANT]),
                      Door("Hidden passage - Kings Room", (1760, 992), [Role.ROYAL, Role.SERVANT]),
                      Door("Hidden passage - Stable", (1760, 1456), [Role.ROYAL, Role.SERVANT])

                      ]
    def draw_rooms(self, screen, camera):
        for room in self.rooms:
            rect = room["rect"].move(-int(camera.x), -int(camera.y))
            pygame.draw.rect(screen,(230,230,230),rect)
            pygame.draw.rect(screen,(255, 118, 189),rect,3)

    def draw_doors(self, screen, camera):
        for door in self.doors:
            x = door.position[0] - camera.x
            y = door.position[1] - camera.y
            if door.is_open:
                color =(0,255,0)
            else:
                color =(0,50,255)
            pygame.draw.circle(screen,color,(int(x),int(y)),7)

    def interact(self, player):
        nearest = min(self.doors, key=lambda d: player.position.distance_to(d.position))
        if player.position.distance_to(nearest.position) <=80:
            nearest.open_door(player.state.role)

    def room_at(self, position):
        position = (position.x, position.y)
        for room in reversed(self.rooms):
            if room["rect"].collidepoint(position):
                return room["name"]
        for passage in self.passage:
            if passage.collidepoint(position):
                return "Hidden Passage"
        return None