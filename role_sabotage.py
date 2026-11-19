from player_state import Role
from goap import Action, Goal
from sabotage import slug
from world_actions import door_edges
ROLE_GOALS = {}
R = Role.ROYAL
LOCKABLE = ["Kings door", "Corridor door"]
CONFISCATE = ["kings_ring", "jewelry", "queens_ring"]

def sabotage_actions(castle):
    actions = []
    for door, a,b in door_edges(castle):
        if door.name in LOCKABLE:
            for room in (a,b):
                actions.append(Action(f"lock {door.name} (from {room})", {"room": room}, {"door_locked_" + slug(door.name): True}, 2, roles={R}, data={"kind": "lock", "door": door.name}))
    for item in CONFISCATE:
        actions.append(Action(f"confiscate {item}", {"opp_visible": True, "opp_has_" + item:True}, {"has_"+item:True}, 1, roles={R}, data={"kind":"confront","mode":"take", "item":item}))
    actions.append(Action("destroy the serum", {"opp_visible": True, "opp_has_truth_serum": True}, {"opp_has_truth_serum":False}, 1, roles={R}, data={"kind": "confront","mode":"destroy", "item": "truth_serum"}))
    barrel = next((o for o in castle.interactable if o.id == "wine_barrel"), None)
    if barrel is not None:
        actions.append(Action("spoil the wine [wine_barrel]", {"room": barrel.room}, {"wine_spoiled": True}, 2, roles={R}, data={"kind":"sabotage", "what":"spoil", "object": "wine_barrel"}))
    return actions