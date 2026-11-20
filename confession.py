from player_state import Role
SUSPICION_LIMIT = 2
BASE_SUSPICION = 2
TOAST_BONUS = 2
EVIDENCE_BONUS = 2
ANNOUNCED = "announce_king_death"
EVIDENCE = ["overturned_cup", "empty_bottle", "suspicious_robe", "letters"]

def evidence_count(character):
    return sum(1 for i in EVIDENCE if character.inventory.has(i))
def suspicion_of(royal, giver):
    s= BASE_SUSPICION
    if royal.has_flag(ANNOUNCED):
        s -= TOAST_BONUS
    if evidence_count(giver) >= 2:
        s -= EVIDENCE_BONUS
    return s + royal.suspicion

def royal_accepts(royal, giver):
    return suspicion_of(royal, giver) < SUSPICION_LIMIT

def decision_cup(giver,royal,  world, accepted):
    world.pending_cup = None
    if accepted:
        giver.inventory.remove_item("spiked_wine")
        royal.set_flag("drank_truth_serum")
        giver.set_flag("royal_confessed")
        world.result = {"winner": "servant", "text":" The Royal drinks... and begins to confess everything. ROYAL: I... I had my father taken... away... I WANTED THE THRONE FOR MYSELF!!! I DESERVE IT!!..."}
        return "The Royal drinks the wine... and begins to confess everything."
    royal.suspicion += 1
    return "The Royal refuses the cup and looks at you suspiciously."
def offer_cup(giver, royal, world):
    if giver.state.role != Role.SERVANT:
        return "Only a servant can serve a Royal."
    if not giver.inventory.has("spiked_wine"):
        return "You have nothing to offer."
    if getattr(royal, "is_player", False):
        world.pending_cup = {"giver": giver, "royal": royal}
        return "A Servant offers you a cup of wine."
    return decision_cup(giver, royal, world, royal_accepts(royal, giver))

