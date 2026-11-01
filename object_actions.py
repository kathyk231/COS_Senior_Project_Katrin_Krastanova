from player_state import Role
EVIDENCE_ITEMS = ["overturned_cup", "empty_bottle", "suspicious_robe", "letters"]
COUP_REQUIREMENTS = ["buried_" + i for i in EVIDENCE_ITEMS]

def reveal_passage(character, painting, world=None):
    king_side=next(d for d in world.doors if d.name== "Hidden passage - Kings Room")
    first_time = king_side.hidden
    for door in world.doors:
        if door.name.startswith("Hidden passage"):
            door.hidden = False
    character.set_flag("found_passage")
    king_side.open_door(character)
    if first_time:
        return "The painting swings aside. A hidden passage is revealed. Enter at your own risk."
    return "The passage is open."

def evidence_action(clue_text, gone_text,take_text,item=None, needs=None, needs_text=""):
    def use(character, obj, world=None):
        if obj.looted:
            if character.state.role == Role.SERVANT and not character.has_flag("searched_" + obj.id):
                character.set_flag("missed_" + obj.id)
            return gone_text
        if character.state.role == Role.SERVANT:
            character.set_flag("searched_" + obj.id)
            return clue_text
        if needs:
            if not character.inventory.has(needs):
                return needs_text
            character.inventory.remove_item(needs)
        obj.looted=True
        if item:
            character.inventory.add_item(item)
        character.set_flag("removed_" + obj.id)
        return take_text
    return use
def deliver_action(item,flag,done_text,missing_text, repeat_text="You already did that"):
    def use(character, obj, world=None):
        if character.has_flag(flag):
            return repeat_text
        if not character.inventory.remove_item(item):
            return missing_text
        character.set_flag(flag)
        return done_text
    return use
def bury_evidence(character,spot, world=None):
    buried = spot.data.setdefault("buried",[])
    if character.state.role != Role.ROYAL:
        return "The soil here looks freshly dug." if buried else "Nothing suspicious here."
    if not character.inventory.has("spade"):
        return "You need a spade to dig here."
    carried = [i for i in EVIDENCE_ITEMS if character.inventory.has(i)]
    if not carried:
        return "You have nothing to bury."
    for item in carried:
        character.inventory.remove_item(item)
        character.set_flag("buried_" + item)
        buried.append(item)
    return "You dig a hole and bury " + ", ".join(i.replace("_"," ") for i in carried) + "."

def announce_king_death(character, podium, world=None):
    if character.state.role != Role.ROYAL:
        return "Only the Royal is allowed to address the Court."
    if not character.inventory.has("kings_ring"):
        return "Without the kings ring, nobody would believe you."
    if character.has_flag("announce_king_death"):
        return "You already addressed the court."
    if any(not character.has_flag(f) for f in COUP_REQUIREMENTS):
        return "You can't announce it yet, there is still evidence out there."
    character.set_flag("announce_king_death")
    return "You announce the kings death to the court."

def sit_on_the_throne(character,seat,world=None):
    if character.state.role != Role.ROYAL:
        return "You may not sit on the throne."
    if not character.has_flag("announce_king_death"):
        return "First announce the kings death to the court on the podium."
    if world.coronation:
        return "You are already seated."
    world.coronation = {"who": character, "left": world.CORONATION_TIME}
    return "You sit on the throne. Stay beside it for 10 seconds to claim it."