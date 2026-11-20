SIGHT = 800
MEMORY_TIME = 8.0
LOCK_TIME = 45.0
SPOIL_TIME = 60.0
def lock_door(character, door, castle):
    if castle.time - getattr(door, "last_lock", -999.0) < 90.0:
        return "You can't lock the door it needs time to reset.."
    for c in castle.characters:
        if c is not character and c.position.distance_to(door.position) < 70:
            return "The door is being used."
    door.locked = True
    door.locked_by = character.name
    door.lock_until = castle.time + LOCK_TIME
    door.last_lock = castle.time
    return f"{character.name} locks the {door.name}"
def unlock_door(character, door, castle):
    door.locked = False
    door.locked_by = None
    character.flags.discard("blocked_" + slug(door.name))
    return f"{character.name} forces the {door.name} open."
def observe(character, castle):
    spot = next((o for o in castle.interactable if o.id == "burial_spot"), None)
    if spot is not None and character.room == spot.room and spot.data.get("buried"):
        character.set_flag("saw_fresh_soil")
def spoil_wine(character, barrel, castle):
    barrel.data["blocked_until"] = castle.time + SPOIL_TIME
    barrel.data["blocked_text"] = "The wine smells off. Someone has tampered with it. You must wait for the barrel to be changed."
    return f"{character.name} spoils the wine."
def confront(royal, victim, mode, item, castle):
    if not victim.inventory.remove_item(item):
        return f"{victim.name} is not carrying the {item}"
    name = item.replace("_", "")
    if mode == "destroy":
        if item == "truth_serum":
            victim.flags.discard("brewed_truth_serum")
            for o in castle.interactable:
                if o.room == "Witch House":
                    o.reset_for(victim)
        castle.notify(victim, f"The royal destroys your {name}!")
        return f"{royal.name} destroys {victim.name}'s {name}."
    royal.inventory.add_item(item)
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