from castle import Castle
from Navmesh_manager import NavmeshManager
from ai_movement import NavGrid
from npcs import create_r_standin

def create_world(with_standin = False):
    castle = Castle()
    if with_standin:
        castle.interactable.append(create_r_standin())
    navmesh = NavmeshManager()
    solids = [o.rect for o in castle.interactable if o.solid]
    solids += [p.rect for p in castle.props if p.solid]
    navmesh.bake(castle.rooms,castle.doors, castle.passage, solids)
    grid = NavGrid(navmesh, castle.width, castle.height)
    anchors = {r["name"]: grid.anchor(r["rect"].center) for r in castle.rooms}
    anchors["Hidden Passage"] = grid.anchor(castle.passage[0].center)
    return castle, navmesh, grid, anchors