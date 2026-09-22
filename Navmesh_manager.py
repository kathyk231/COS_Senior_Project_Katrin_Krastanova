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
        print("Vertices:",self.vertices)
        print("Polygons:",self.polygons)
        self.pathfinder = pf.PathFinder(self.vertices, self.polygons)
