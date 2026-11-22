from settings import cfg
SIGHT = 800
MEMORY_TIME = 8.0
SPOIL_TIME = 60.0
SPOIL_COOLDOWN = 150.0
MAX_DESTROYS = 1
PATROL_ROOMS = ["Woods", "Kings Room", "Entrance Hall", "Throne Room"]
def mark(castle, key):
    castle.sabotage.setdefault(key, []).append(castle.time)
def spoil_ready(castle):
    times = castle.sabotage.get("spoil", [])
    return not times or castle.time - times[-1] >= SPOIL_COOLDOWN
def destroy_ready(castle):
    return len(castle.sabotage.get("destroy", [])) < MAX_DESTROYS
def lock_door(character, door, castle):
    if castle.time - getattr(door, "last_lock", -999.0) < 90.0:
        return "You can't lock the door it needs time to reset.."
    for c in castle.characters:
        if c is not character and c.position.distance_to(door.position) < 70:
            return "The door is being used."
    door.locked = True
    mark(castle, "lock")
    door.locked_by = character.name
    door.lock_until = castle.time + cfg.lock_time
    door.last_lock = castle.time
    return f"{character.name} locks the {door.name}"
def unlock_door(character, door, castle):
    door.locked = False
    mark(castle, "unlock")
    door.locked_by = None
    character.flags.discard("blocked_" + slug(door.name))
    return f"{character.name} forces the {door.name} open."
def fresh_facts(character, castle):
    visits = character.__dict__.get("visits", {})
    return {"fresh_" +slug(r): True for r in PATROL_ROOMS if castle.time -visits.get(r,-1e9)<cfg.patrol_interval}
def observe(character, castle):
    if character.room:
        character.__dict__.setdefault("visits", {})[character.room] = castle.time
    spot = next((o for o in castle.interactable if o.id == "burial_spot"), None)
    if spot is not None and character.room == spot.room and spot.data.get("buried"):
        character.set_flag("saw_fresh_soil")
def spoil_wine(character, barrel, castle):
    mark(castle, "spoil")
    barrel.data["blocked_until"] = castle.time + SPOIL_TIME
    barrel.data["blocked_text"] = "The wine smells off. Someone has tampered with it. You must wait for the barrel to be changed."
    return f"{character.name} spoils the wine."
def confront(royal, victim, mode, item, castle):
    if not victim.inventory.remove_item(item):
        return f"{victim.name} is not carrying the {item}"
    name = item.replace("_", " ")
    if mode == "destroy":
        mark(castle, "destroy")
        if item == "truth_serum":
            victim.flags.discard("brewed_truth_serum")
            for o in castle.interactable:
                if o.room == "Witch House":
                    o.reset_for(victim)
        castle.notify(victim, f"The royal destroys your {name}!")
        return f"{royal.name} destroys {victim.name}'s {name}."
    royal.inventory.add_item(item)
    mark(castle, "confiscate")
    castle.notify(victim, f"The royal confiscates your {name}!")
    return f"{royal.name} confiscates {victim.name}'s {name}."
def sees(a, b):
    return a.room is not None and a.room == b.room and a.position.distance_to(b.position) <= SIGHT
def slug(text):
    return "".join(ch if ch.isalnum() else "_" for ch in text.lower())

def opponent_facts(me, others):
    facts = {}
    for other in others:
        if other is me or other.state.role == me.state.role:
            continue
        if sees(me, other):
            facts["opp_visible"] = True
            facts["opp_in_" + slug(other.room)] = True
            for item in other.inventory.names():
                facts["opp_has_" + item] = True
    return facts