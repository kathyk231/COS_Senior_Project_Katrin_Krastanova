from player_state import Role
EVIDENCE_ITEMS = ["overturned_cup", "empty_bottle", "suspicious_robe", "letters"]
COUP_REQUIREMENTS = ["buried_", + i for i in EVIDENCE_ITEMS]

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
            return gone_text
        if character.state.role == Role.SERVANT:
            character.set_flag("searched_" + obj.id)
            return clue_text
        if needs:
            if not character.inventory.has(needs):
                return needs_text
            character.inventory.remove(needs)
        obj.looted=True
        if item:
            character.inventory.add(item)
        character.set_flag("removed_" + obj.id)
        return take_text
    return use
