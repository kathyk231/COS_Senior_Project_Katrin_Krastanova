from player_state import Role
from settings import cfg
SUSPICION_LIMIT = 2
ANNOUNCED = "announce_king_death"
EVIDENCE = ["overturned_cup", "empty_bottle", "suspicious_robe", "letters"]

def evidence_count(character):
    return sum(1 for i in EVIDENCE if character.inventory.has(i))
def suspicion_of(royal, giver):
    s= cfg.base_suspicion
    if royal.has_flag(ANNOUNCED):
        s -= cfg.toast_bonus
    if evidence_count(giver) >= 2:
        s -= cfg.evidence_bonus
    return s + royal.suspicion

def royal_accepts(royal, giver):
    judged = suspicion_of(royal,giver) + cfg.rng_judge.gauss(0.0,cfg.suspicion_noise)
    return judged < SUSPICION_LIMIT

def decision_cup(giver,royal,  world, accepted):
    if not cfg.quiet:
        print(f"[cup] evidence {evidence_count(giver)}, suspicion {suspicion_of(royal, giver):.1f}, refusals so far {royal.suspicion}, accepted {accepted}")
    world.pending_cup = None
    if accepted:
        how = [n for n,ok in (("toast", royal.has_flag(ANNOUNCED)),("evidence", evidence_count(giver) >= 2)) if ok]
        giver.inventory.remove_item("spiked_wine")
        royal.set_flag("drank_truth_serum")
        giver.set_flag("royal_confessed")
        world.result = {"winner": "servant","how": "+".join(how) or "lucky", "text":" The Royal drinks... and begins to confess everything. ROYAL: I... I had my father taken... away... I WANTED THE THRONE FOR MYSELF!!! I DESERVE IT!!..."}
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

