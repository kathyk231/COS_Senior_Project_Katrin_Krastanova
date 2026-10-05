import pygame
from door import Door
from player_state import Role

class Castle:
    def __init__(self):
        self.width = 2604
        self.height = 2000
        self.rooms = []
        self.doors = []
        self.passage =[pygame.Rect(1740, 990, 40, 466)]
        self.create_castle()
        self.create_doors()

    def create_castle(self):
        self.rooms =[
            {"name": "Great Hall/Throne Room",
             "rect": pygame.Rect(588, 326,960, 664)},
            {"name": "Kings Bedroom",
             "rect": pygame.Rect(1546, 326, 432, 664)},
            {"name": "Corridor",
             "rect": pygame.Rect(3, 563, 587, 136)},
            {"name": "Kitchen",
             "rect": pygame.Rect(3, 1270, 587, 499)},
            {"name": "Queens Room",
             "rect": pygame.Rect(3, 698, 587, 573)},
            {"name": "Royal Room",
             "rect": pygame.Rect(3, 5, 587, 560)},
            {"name": "Stable",
             "rect": pygame.Rect(1547,1456, 431, 541)},
            {"name": "Woods",
             "rect": pygame.Rect(1976, 0, 623, 1997)},
            {"name": "Entrance Hall",
             "rect": pygame.Rect(588, 988, 961, 1009)},
            {"name": "Witch House",
             "rect": pygame.Rect(2088, 0, 511, 478)}
        ]
    def create_doors(self):
        self.doors = [Door("Kitchens door",(588,1450),[Role.SERVANT]),
                      Door("Throne Room door",(1068, 989), [Role.ROYAL, Role.SERVANT]),
                      Door("Royal Room door",(295, 563), [Role.ROYAL]),
                      Door("Kings door",(1547,650), [Role.ROYAL]),
                      Door("Queens Room door",(295, 698), [Role.ROYAL]),
                      Door("Entrance hall main door", (1068, 1997), [Role.SERVANT, Role.ROYAL]),
                      Door("Stable door", (1547, 1725), [Role.ROYAL, Role.SERVANT]),
                      Door("Corridor door", (588, 630), [Role.ROYAL, Role.SERVANT]),
                      Door("Woods entrance", (1976, 1870), [Role.ROYAL, Role.SERVANT]),
                      Door("Witch house door", (2340, 478), [Role.ROYAL, Role.SERVANT]),
                      Door("Hidden passage - Kings Room", (1760, 990), [Role.ROYAL, Role.SERVANT]),
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
        if player.position.distance_to(nearest.position) <=50:
            nearest.open_door(player.state.role)