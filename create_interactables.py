from interactable import Interactable
def create_interactables():
    I = Interactable
    return [
    I("vanity", "Vanity",(400,16, 176, 100), "Royal Room",
    gives = "jewelry", found_text="You find jewelry in the vanity.",empty_text="This vanity is empty.", solid =True)
    ]