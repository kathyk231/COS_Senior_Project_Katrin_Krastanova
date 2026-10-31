TRUTH_SERUM = ["potion_bottle","truth_berry", "light_essence","tooth_leaf","phoenix_feather"]
SPIKED_WINE = ["truth_serum", "wine", "wine_cup"]
def brew_truth_serum(character, cauldron):
    if cauldron.looted:
        return "The cauldron is empty."
    missing = [i for i in TRUTH_SERUM if not character.inventory.has(i)]
    if missing:
        names =",".join(m.replace("_"," ") for m in missing)
        return f"The recipe is not complete. You need {names}."
    for item in TRUTH_SERUM:
        character.inventory.remove(item)
    character.inventory.add("truth_serum")
    character.set_flag("brewed_truth_serum")
    cauldron.looted = True
    return "The cauldron glows and sparkles. You put the serum in the bottle and take it. "

def mix_spiked_wine(character, table):
    missing = [i for i in SPIKED_WINE if not character.inventory.has(i)]
    if missing:
        names =",".join(m.replace("_"," ") for m in missing)
        return f"You still need {names}."
    for item in SPIKED_WINE:
        character.inventory.remove(item)
    character.inventory.add("spiked_wine")
    character.set_flag("mixed_spiked_wine")
    return "You pour the wine and the serum into the cup. It looks perfectly normal. You take it "