from interactable import Interactable
from prop import Prop
def create_interactables():
    I = Interactable
    return [
    I("vanity", "Vanity",(404,12, 176, 100), "Royal Room",
    gives = "jewelry", found_text="You find jewelry in the vanity.",empty_text="This vanity is empty.", solid =True),
    I("cupboard","Clothes cupboard",(480,328,100,228), "Royal Room",verb = "Investigate",
    found_text = "You find the Royals' clothes, but one robe is missing."),
    I("nightstand","Royal nightstand",(192,12,64,80),"Royal Room",verb="Search", gives= "empty_bottle",
      found_text="You rummage through the nightstand and you find an empty sleeping potion bottle. You take it.",
      empty_text="There is nothing left in here.")
    ]
def create_props():
    P = Prop
    return[
        P("royal_bed", (8,12,184,264), "Royal Room")
    ]