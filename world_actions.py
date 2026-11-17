import pygame
from goap import Action
from player_state import Role

ROLES = list(Role)
SERUM = ["potion_bottle", "truth_berry", "light_essence", "tooth_leaf", "phoenix_feather"]
EVIDENCE = ["overturned_cup", "empty_bottle", "suspicious_robe", "letters"]

def world_facts(castle):
    facts = {}
    if any(d.name.startswith("Hidden passage") and not d.hidden for d in castle.doors):
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
            if src not in anchors or dst not in anchors:
                continue
            dist = anchors[src].distance_to(anchors[dst])
            cost = round(1+dist / 300, 1)
            for role in ROLES:
                for label, extra in door_options(door, role):
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
    specials = special_actions(castle)
    skip = {a.data["object"] for a in specials}
    return door_actions(castle, anchors) + plain_object_actions(castle, skip) + specials
def special_actions(castle):
    where = {o.id: o.room for o in castle.interactable}
    R, S = Role.ROYAL, Role.SERVANT
    out = []
    def AS(label, obj, pre, eff, roles = None, cost=1, kind = "use", wait=0, item= None):
        if obj not in where:
            return
        data = {"kind": kind, "object": obj}
        if wait:
            data["wait"] = wait
        if item:
            data["item"] = item
        out.append(Action(f"{label} [{obj}]", {"room":where[obj],**pre}, eff, cost, roles=roles, data=data))
    for obj, item in (("royal_nightstand", "empty_bottle"), ("queen_desk", "letters"), ("king_nightstand", "overturned_cup"), ("king_vanity", "suspicious_robe")):
        AS("examine", obj, {},{"searched_" + obj: True}, roles={S}),
        AS("take evidence", obj, {}, {"has_" +item: True}, roles={R})
    AS("examine", "king_carpet", {}, {"searched_king_carpet": True}, roles={S})
    AS("scrub", "king_carpet", {"has_water":True}, {"removed_king_carpet":True, "has_water":False}, roles={R})
    AS("move the painting", "painting", {}, {"found_passage": True, "passage_revealed": True})
    AS("pour water", "horse_trough", {"has_water": True}, {"watered_horses":True, "has_water":False}, roles={S})
    AS("fill rack", "feeding_rack", {"has_hay": True}, {"fed_horses": True, "has_hay":False}, roles={S})
    AS("mix spiked wine", "kitchen_table", {"has_truth_serum": True, "has_wine_cup": True, "has_wine": True}, {"has_spiked_wine": True, "mixed_spiked_wine": True, "has_truth_serum": False, "has_wine_cup": False, "has_wine": False}, roles={S})
    AS("brew serum", "cauldron", {"has_" + i: True for i in SERUM},{"has_truth_serum":True, "brewed_truth_serum": True, **{"has_" + i: False for i in SERUM}}, roles= {S})
    AS("give wine", "king_guard", {"has_wine": True}, {"guard_drunk": True, "has_wine": False}, roles= {S}, kind= "give", item="wine", cost=4)
    AS("talk to the farmer", "stable_guy", {}, {"talked_stable_guy": True})
    AS("hear farmer story", "stable_guy", {"watered_horses": True, "fed_horses": True}, {"knows_secret_bag": True}, roles={S})
    AS("offer spiked wine", "royal_npc", {"has_spiked_wine": True}, {"royal_confessed": True, "has_spiked_wine": False}, roles= {S}, kind= "give", item="spiked_wine", cost=2)
    for item in ("jewelry", "queens_ring"):
        AS(f"bribe with {item}", "king_guard", {"has_" + item: True}, {"bribed_guard": True, "has_" + item:False}, kind="give", item=item)
    for item in ("queens_ring", "jewelry"):
        AS(f"bribe with {item}", "stable_guy", {"has_" +item: True}, {"bribed_stable_guy":True,"has_"+item:False},roles={R}, kind="give", item=item)
    AS("bury evidence", "burial_spot", {"has_spade": True,**{"has_"+i: True for i in EVIDENCE}},{**{"buried_"+i:True for i in EVIDENCE}, **{"has_" +i: False for i in EVIDENCE}}, roles={R})
    for obj in ("podium_speech", "podium_speech_2"):
        AS("announce death", obj, {"has_kings_ring": True, **{**{"buried_"+i:True for i in EVIDENCE}}}, {"announce_king_death": True}, roles={R})
    AS("sit on throne", "throne_seat",{"announce_king_death": True}, {"crowned": True}, roles={R}, wait= 14)
    AS("order guard", "king_guard", {}, {"bribed_guard": True}, roles={R}, kind= "give", item="order", cost=4)
    AS("order farmer", "stable_guy", {}, {"bribed_stable_guy": True}, roles={R}, kind= "give", item="order", cost=4)
    return out

