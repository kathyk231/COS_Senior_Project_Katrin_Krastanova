import pygame
import pathfinder as pf
from pathfinder import navmesh_baker

class NavmeshManager:
    def __init__(self):
        self.vertices = []
        self.polygons = []
        self.pathfinder = None
    def bake(self, rooms):
        vertices = []
        polygons = []
        for room in rooms:
            rect = room["rect"]
            start_index= len(vertices)
            vertices.extend([(rect.left,0,rect.top), (rect.right,0,rect.top),(rect.right,0,rect.bottom), (rect.left, 0,rect.bottom)])
            polygons.append([start_index,start_index+1,start_index+2,start_index+2 ])
            passage_left = 1740
            passage_right = 1780
            passage_top =990
            passage_bottom= 1456
            vertices.extend([(passage_left,0,passage_top),(passage_right,0,passage_top),(passage_right,0,passage_bottom),(passage_left,0,passage_bottom)])
            polygons.append([start_index, start_index + 1, start_index + 2, start_index + 2])
        baker = navmesh_baker.NavmeshBaker()
        baker.add_geometry(vertices,polygons)
        baker.bake(
            cell_size=5,
            cell_height=5,
            agent_height=14,
            agent_radius=7
        )
        self.vertices,self.polygons = (baker.get_polygonization())
        self.pathfinder = pf.PathFinder(self.vertices, self.polygons)
    def draw(self, screen,camera):
        if self.pathfinder is None:
            return
        for polygon in self.polygons:
            points = []
            for vertex_index in polygon:
                vertex = self.vertices[vertex_index]
                x = vertex[0] - camera.x
                y = vertex[2] - camera.y
                points.append((int(x),int(y)))
            if len(points) >= 3:
                pygame.draw.polygon(screen,(255,255,206),points)
                pygame.draw.lines(screen,(107, 44, 255), True, points,2)
    def is_walkable(self, position):
        if self.pathfinder is None:
            return True
        point = (position.x, 0, position.y)
        result = self.pathfinder.sample(point)
        return result is not None

