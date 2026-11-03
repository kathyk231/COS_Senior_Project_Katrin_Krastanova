from player_state import Role
SUSPICION_LIMIT = 2
BASE_SUSPICION = 2
TOAST_BONUS = 2

def suspicion_of(royal, giver):
    s= BASE_SUSPICION
    if royal.has_flag("announced_king_death"):
        s += TOAST_BONUS
    s += royal.suspicion
    return s

def royal_accepts(royal, giver):
    return suspicion_of(royal, giver) < SUSPICION_LIMIT

def decision_cup(giver,royal,  world, accepted):
    if accepted:
        giver.inventory.remove_item("spiked_wine")
        royal.set_flag("drank_truth_serum")
        world.result = {"winner": "servant", "text":" The Royal drinks... and confesses everything."}
        return "The Royal drinks the wine... and begins to confess everything."
    royal.suspicion += 1
    return "The Royal refuses the cup and looks at you suspiciously."
def offer_cup(giver, royal, world):
    if giver.state.role != Role.SERVANT:
        return "Only a servant can serve a Royal."
    if not giver.inventory.has("spiked_wine"):
        return "You have nothing to offer."
    return decision_cup(giver, royal, world, royal_accepts(royal, giver))

