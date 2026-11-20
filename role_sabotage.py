from player_state import Role
from goap import Action, Goal
from sabotage import slug
from world_actions import door_edges, EVIDENCE

R = Role.ROYAL
LOCKABLE = ["Kings door", "Corridor door"]
CONFISCATE = ["kings_ring", "jewelry", "queens_ring"] + EVIDENCE

def sabotage_actions(castle):
    actions = []
    for door, a,b in door_edges(castle):
        if door.name not in LOCKABLE:
            continue
        fact = "door_locked_" + slug(door.name)
        for room in (a,b):
            actions.append(Action(f"lock {door.name} (from {room})", {"room": room}, {"door_locked_" + slug(door.name): True}, 2, roles={R}, data={"kind": "lock", "door": door.name}))
            actions.append(Action(f"unlock {door.name} (from {room})", {"room": room, fact: True}, {fact: True}, 2, roles={S}, data={"kind": "unlock", "door": door.name}))

    for item in CONFISCATE:
        actions.append(Action(f"confiscate {item}", {"opp_visible": True, "opp_has_" + item:True}, {"has_"+item:True}, 1, roles={R}, data={"kind":"confront","mode":"take", "item":item}))
    actions.append(Action("destroy the serum", {"opp_visible": True, "opp_has_truth_serum": True}, {"opp_has_truth_serum":False}, 1, roles={R}, data={"kind": "confront","mode":"destroy", "item": "truth_serum"}))
    barrel = next((o for o in castle.interactable if o.id == "wine_barrel"), None)
    if barrel is not None:
        actions.append(Action("spoil the wine [wine_barrel]", {"room": barrel.room}, {"wine_spoiled": True}, 2, roles={R}, data={"kind":"sabotage", "what":"spoil", "object": "wine_barrel"}))
    return actions

def royal_goals():
    alert = lambda s: s.get("alert", 0)
    goals = [
        Goal("destroy the serum", {"opp_has_truth_serum": False}, lambda s: 9 if s.get("opp_has_truth_serum") else 0),
        Goal("lock the Kings door", {"door_locked_kings_door": True}, lambda s: 6 if s.get("opp_in_throne_room") or s.get("opp_in_entrance_hall") else 0),
        Goal("lock the Corridor door", {"door_locked_corridor_door": True}, lambda s: 5 if s.get("opp_in_corridor") else 0),
        Goal("spoil the wine", {"wine_spoiled": True}, lambda s: 7 if s.get("opp_has_truth_serum") or alert(s) >= 7 else 0),
        Goal("retake the king's ring", {"has_kings_ring":True}, lambda s: 8 if s.get("opp_has_kings_ring") else 0),
        Goal("retake the jewelry", {"has_jewelry": True}, lambda s: 5 if s.get("opp_has_jewelry") else 0),
        Goal("silence the guard", {"bribed_guard": True}, lambda s: 4 if alert(s) >= 2 else 0),
        Goal("silence the farmer", {"bribed_stable_guy": True}, lambda s: 4 if alert(s) >= 3 else 0),
        Goal("remove the robe", {"removed_king_vanity": True}, lambda s: 3 if alert(s) >= 4 else 0),
        Goal("remove the cup", {"removed_king_nightstand": True}, lambda s: 3 if alert(s) >= 4 else 0),
        Goal("secure the king's ring", {"has_kings_ring": True}, lambda s: 4 if alert(s) >= 3 else 0),
        Goal("clean the blood", {"removed_king_carpet": True}, lambda s: 3 if alert(s) >= 4 else 0),
        Goal("hide the bottle", {"removed_royal_nightstand": True}, lambda s: 3 if alert(s) >= 4 else 0)
    ]
    for item in EVIDENCE:
        goals.append(Goal(f"retake the {item}", {"has_" + item:True}, lambda s, i=item: 8 if s.get("opp_has_" + i) else 0))
    return goals
def servant_goals():
    alert = lambda s: s.get("alert", 0)
    noticed_missing = lambda s: any(s.get(k) for k in ("missed_king_nightstand", "missed_king_vanity", "missed_king_carpet", "missed_royal_nightstand"))
    goals = []
    for door in LOCKABLE:
        fact, blocked = "door_locked_" + slug(door), "blocked_" + slug(door)
        goals.append(Goal(f"unlock the {door}", {fact: False}, lambda s, f=fact, b=blocked: 6 if s.get(b) and s.get(f) else 0))
    goals += [
        Goal("grab the kings ring", {"has_kings_ring": True}, lambda s: 4 if (s.get("bribed_guard") or s.get("guard_drunk")) and not s.get("missed_king_bed") and not s.get("has_kings_ring") else 0),
        Goal("check the loose soil", {"saw_fresh_soil": True}, lambda s: 3 if (noticed_missing(s) or alert(s) >= 3) and not s.get("saw_fresh_soil") else 0),
        Goal("dig up the evidence", {"evidence_in_hand": True}, lambda s: 5 if s.get("saw_fresh_soil") else 0)
    ]
    return goals
ROLE_GOALS = {Role.ROYAL: royal_goals, Role.SERVANT: servant_goals()}
