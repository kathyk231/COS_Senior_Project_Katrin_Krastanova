import pygame
import pathfinder as pf
from pathfinder import navmesh_baker

class NavmeshManager:
    def __init__(self):
        self.vertices = []
        self.polygons = []
        self.pathfinder = None
    def bake(self,vertices,polygons):
        baker = navmesh_baker.NavmeshBaker()
        baker.add_geometry(vertices,polygons)
        baker.bake()
        (self.vertices,self.polygons) = baker.get_polygonization()
        self.pathfinder = pf.PathFinder(self.vertices, self.polygons)
    def draw(self, screen):
        for polygon in self.polygons:
            points = []
            for vertex_index in polygon:
                vertex = self.vertices[vertex_index]
                x = vertex[0]* 80 +500
                y = vertex[2]* 70 +300
                points.append((x,y))
            if len(points) >= 3:
                pygame.draw.polygon(screen,(255,255,206),points)
                pygame.draw.lines(screen,(107, 44, 255), True, points,2)
