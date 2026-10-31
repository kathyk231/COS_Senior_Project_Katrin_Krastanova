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