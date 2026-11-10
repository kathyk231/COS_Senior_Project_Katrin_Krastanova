import pygame
import heapq

CELL = 16
DIRS = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)]

class NavGrid:
    def __init__(self, navmesh, width, height, cell=CELL, radius=12):
        self.cell = cell
        self.navmesh = navmesh
        self.cols = width // cell +1
        self.rows = height // cell +1
        self.radius = radius
        self.free= set()

    def build(self):
        for cy in range(self.rows):
            for cx in range(self.cols):
                x,y = self.center(cx,cy)
                if self.navmesh.body_free(x, y, self.radius):
                    self.free.add((cx,cy))
    def cell_of(self,p):
        return (int(p[0] / self.cell),int(p[1] / self.cell))
    def center(self,cx,cy):
        return ((cx*0.5)*self.cell,(cy*0.5)*self.cell)
