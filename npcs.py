from interactable import Interactable
from player_state import Role

GUARD_BRIBES = ["jewelry", "queens_ring"]
FARMER_BRIBES = [ "queens_ring", "jewelry"]

def talk_guard(character, npc, world= None):
    character.set_flag("talked_" +npc.id)
    if character.state.role == Role.ROYAL:
        return "Guard: Your Highness. The King's Room is sealed, as you ordered."
    return "Guard: Halt. The King's Room is closed for servants."

def talk_stable_guy(character, npc, world=None):
    character.set_flag("talked_" +npc.id)
    if character.state.role == Role.ROYAL:
        if character.has_flag("bribed_stable_guy"):
            return "Farmer: My highness, my lips are sealed."
        return "Farmer: My highness, is something wrong?."
    if not (character.has_flag("watered_horses") and character.has_flag("fed_horses")):
        return "Farmer: Water in the trough, hay in the rack. Then we can talk."
    if npc.data.get("silenced"):
        return "Farmer: I... I am sorry I can't say anything. Please leave."
    character.set_flag("knows_secret_bag")
    character.set_flag("sent_to_witch")
    return "Farmer: A guard hauled a huge back through the tunnel you came from. It bore the Royal crest. Follow the mushroom trail to the witch for a Truth Serum."
def give_guard(character, guard, world=None):
    role = character.state.role
    if character.has_flag("bribed_guard"):
        return "Guard: Coming to pay again?"
    if character.has_flag("guard_drunk"):
        return "Guard: I can't drink anymore."
    if role == Role.SERVANT and character.inventory.remove_item("wine"):
        character.set_flag("guard_drunk")
        return "The guard takes the wine and dozes off. You can sneak past him now."
    if role == Role.SERVANT and guard.data.get("paid_by") == "royal":
        return "Guard: I serve only the Royal. I won't accept anything from you."
    for item in GUARD_BRIBES:
        if character.inventory.remove_item(item):
            character.set_flag("bribed_guard")
            guard.data.setdefault("paid_by", role.value)
            name = item.replace("_", " ")
            if role == Role.ROYAL:
                return f"The guard takes the {name}. He will keep quiet"
            return f"The guard takes the {name} and looks away. You may pass."
    return "You have nothing to offer the guard."
def give_stable_guy(character, npc, world=None):
    if character.state.role != Role.ROYAL:
        return "Farmer: Keep your coin, help me with my chores and I will help you."
    if character.has_flag("bribed_stable_guy"):
        return "Farmer: My Highness, my lips are sealed."
    for item in FARMER_BRIBES:
        if character.inventory.remove_item(item):
            character.set_flag("bribed_stable_guy")
            npc.data["silenced"] = True
            name = item.replace("_", " ")
            return f"The farmer pockets the {name}. He will keep quiet."
    return "You have nothing to offer the guard."


def create_npcs():
    I = Interactable
    return [
        I("king_guard","King's Guard", (1480,540, 40,52),"Throne Room", verb= "Talk", color=(60,80,160),
          use=talk_guard, on_give=give_guard),
        I("stable_guy", "Farmer", (1736,1740,40,52), "Stable", verb= "Talk", color=(60,80,160),
          use=talk_stable_guy, on_give=give_stable_guy)
    ]