import pygame
from goap import Action
from player_state import Role

ROLES = list(Role)

def world_facts(castle):
    facts = {}
    if any(d.name.startswith("Hidden Passage") and not d.hidden for d in castle.doors):
        facts["passage_revealed"] = True
    return facts
def sense_state(character, castle):
    state = character.facts()
    state.update(world_facts(castle))
    return state
def door_options(door, role):
    if role in door.allowed_role:
        return [("role", {})]
    options = []
    if door.key:
        options.append((f"key {door.key}", {"has_" + door.key: True}))
    for flag in door.pass_flags:
        options.append((flag, {flag: True}))
    return options
def door_edges(castle):
    edges = []
    for door in castle.doors:
        x,y = door.position
        for dx,dy in ((40, 0), (0,40)):
            a = castle.room_at(pygame.Vector2(x-dx,y-dy))
            b = castle.room_at(pygame.Vector2(x+dx,y+dy))
            if a and b and a != b:
                edges.append((door, a,b))
                break
    return edges

def door_actions(castle, anchors):
    actions = []
    for door, a, b in door_edges(castle):
        for src, dst in ((a, b), (b, a)):
            if src not in anchors and dst not in anchors:
                continue
            dist = anchors[src].distance_to(anchors[dst])
            cost = round(1+dist / 300, 1)
            for role in ROLES:
                for label, extra in door_options(castle, role):
                    pre = {"room":src, **extra}
                    if door.hidden:
                        pre["passage_revealed"] = True
                    actions.append(Action(f"go {src} -> {dst} ({role.value}: {label})", pre, {"room": dst}, cost, roles={role}, data={"kind": "move", "goto_room":dst}))
    return actions

def plain_object_actions(castle, skip):
    actions = []
    for o in castle.interactable:
        if o.id in skip or o.on_give:
            continue
        if o.use:
            print(f"[world actions] no planner description for '{o.id}', ignoring it.")
            continue
        effects = {"searched_" + o.id: True}
        if o.gives:
            effects["has_" + o.gives] = True
        actions.append(Action(f"{o.verb} {o.name} [{o.id}]",{"room": o.room}, effects, 1, data={"kind": "use", "object": o.id}))
    return actions

def build_world_actions(castle, anchors):
    return door_actions(castle, anchors) + plain_object_actions(castle, skip)
