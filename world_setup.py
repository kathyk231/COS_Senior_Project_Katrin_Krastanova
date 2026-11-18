from castle import Castle
from Navmesh_manager import NavmeshManager
from ai_movement import NavGrid
from npcs import create_r_standin
import pygame

def create_world(royal =None):
    castle = Castle()
    if royal is not None:
        npc = create_r_standin()
        npc.data["character"] = royal
        npc.data["follows"] = royal
        npc.solid = False
        npc.rect.size = (24,24)
        npc.rect.center = (int(royal.position.x), int(royal.position.y))
        npc.sprite = pygame.Surface((1,1), pygame.SRCALPHA)
        castle.interactable.append(npc)
    navmesh = NavmeshManager()
    solids = [o.rect for o in castle.interactable if o.solid]
    solids += [p.rect for p in castle.props if p.solid]
    navmesh.bake(castle.rooms,castle.doors, castle.passage, solids)
    grid = NavGrid(navmesh, castle.width, castle.height)
    anchors = {r["name"]: grid.anchor(r["rect"].center) for r in castle.rooms}
    anchors["Hidden Passage"] = grid.anchor(castle.passage[0].center)
    return castle, navmesh, grid, anchors