SIGHT = 450
MEMORY_TIME = 8.0

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