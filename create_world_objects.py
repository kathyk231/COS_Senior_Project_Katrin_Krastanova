from interactable import Interactable
from prop import Prop
def create_interactables():
    I = Interactable
    return [
    I("vanity", "Vanity",(400,16, 176, 100), "Royal Room",
    gives = "jewelry", found_text="You find jewelry in the vanity.",empty_text="This vanity is empty.", solid =True)
    ]
def create_props():
    P = Prop
    return[
        P("royal_bed", (12,16,184,264), "Royal Room")
    ]