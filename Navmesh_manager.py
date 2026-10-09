import pygame
import pathfinder as pf
from pathfinder import navmesh_baker
WALL =16
DOOR_GAP=96
class NavmeshManager:
    def __init__(self):
        self.areas = []
        self.walls = []
        self.openings = []
        self.pathfinder = None
    def bake(self, rooms, doors, passages):
        self.areas = [r["rect"] for r in rooms] +list(passages)
        self.walls =[]
        h = WALL//2
        for room in rooms:
            rect = room["rect"]
            self.walls += [pygame.Rect(rect.left - h, rect.top - h, rect.width + WALL,WALL),
                           pygame.Rect(rect.left -h, rect.bottom -h, rect.width + WALL,WALL),
                           pygame.Rect(rect.left-h, rect.top-h,WALL, rect.height + WALL),
                           pygame.Rect(rect.right-h,rect.top-h, WALL, rect.height + WALL)]

        self.openings = []
        for door in doors:
            x,y = door.position
            r = pygame.Rect(0,0,DOOR_GAP,DOOR_GAP)
            r.center = x,y
            self.openings.append((door,r))
    def update_doors(self,dt,blocks):
        for door,rect in self.openings:
            blocked = False
            for position, radius in blocks:
                if rect.inflate(radius*2,radius*2).collidepoint(position.x,position.y):
                    blocked = True
                    break
            door.update(dt,blocked)
    def is_walkable(self, position):
        point = (position.x, position.y)
        if not any(a.collidepoint(point) for a in self.areas):
            return False
        if any(w.collidepoint(point) for w in self.walls):
            return any(d.is_open and r.collidepoint(point) for d,r in self.openings)
        return True

    def draw(self, screen,camera):
        off =(-int(camera.x),-int(camera.y))

        for w in self.walls:
            pygame.draw.rect(screen,(70,60,90), w.move(off))
        for door,rect in self.openings:
            if door.is_open:
                for a in self.areas:
                    c = rect.clip(a)
                    if c.width>0 and c.height>0:
                        pygame.draw.rect(screen,(230,230,230), c.move(off))


