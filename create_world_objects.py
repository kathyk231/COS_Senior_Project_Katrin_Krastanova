from interactable import Interactable
from prop import Prop
def create_interactables():
    I = Interactable
    return [
    I("vanity", "Vanity",(404,12, 176, 100), "Royal Room",
    gives = "jewelry", found_text="You find jewelry in the vanity.",empty_text="This vanity is empty.", solid =True),
    I("wardrobe","Wardrobe",(480,328,100,228), "Royal Room",verb = "Investigate",
    found_text = "You find the Royals' clothes, but one robe is missing."),
    I("nightstand","Royal nightstand",(192,12,64,80),"Royal Room", gives= "empty_bottle",
      found_text="You rummage through the nightstand and you find an empty sleeping potion bottle. You take it.",
      empty_text="There is nothing left in here."),
    I("cupboard","Corridor's cupboard",(8,584,28,96),"Corridor",
      found_text="You find something", empty_text="There is nothing more here"),
    I("desk", "Queens Desk", (8,708,72,192),"Queens Room", verb="Investigate",
      found_text="You find suspicious letters between the Queen and the Royal"),
    I("nightstand","Queens nightstand",(504,1064,76,80),"Queens Room", gives= "queens_ring",
      found_text="You find the Queens ring.", empty_text="You searched this already."),
    I("vanity","Queens vanity",(232,1226,124,40),"Queens Room",
      found_text="There is nothing useful here")
    ]
def create_props():
    P = Prop
    return[
        P("carpet",(160,200,240,240),"Royal Room",color=(132,37,197),solid= False),
        P("royal_bed", (8,12,184,264), "Royal Room",sprite="bed"),
        P("couch",(8,360,64,196), "Royal Room"),
        P("recliner",(104,480,80,76), "Royal Room"),
        P("table",(104,320,80,120), "Royal Room"),
        P("carpet",(40,600,524,64),"Corridor", color=(132,37,197),solid= False),
        P("pot_1",(84,572,16,16),"Corridor",sprite="pot"),
        P("pot_2",(120,572,16,16),"Corridor",sprite="pot"),
        P("pot_3", (156, 572, 16, 16), "Corridor", sprite="pot"),
        P("pot_4", (192, 572, 16, 16), "Corridor", sprite="pot"),
        P("pot_5", (84, 676, 16, 16), "Corridor", sprite="pot"),
        P("pot_6", (120, 676, 16, 16), "Corridor", sprite="pot"),
        P("pot_7", (156, 676, 16, 16), "Corridor", sprite="pot"),
        P("pot_8", (192, 676, 16, 16), "Corridor", sprite="pot"),
        P("pot_9", (364, 572, 16, 16), "Corridor", sprite="pot"),
        P("pot_10", (400, 572, 16, 16), "Corridor", sprite="pot"),
        P("pot_11", (436, 572, 16, 16), "Corridor", sprite="pot"),
        P("pot_12", (472, 572, 16, 16), "Corridor", sprite="pot"),
        P("pot_13", (508, 572, 16, 16), "Corridor", sprite="pot"),
        P("pot_14", (364, 676, 16, 16), "Corridor", sprite="pot"),
        P("pot_15", (400, 676, 16, 16), "Corridor", sprite="pot"),
        P("pot_16", (436, 676, 16, 16), "Corridor", sprite="pot"),
        P("pot_17", (472, 676, 16, 16), "Corridor", sprite="pot"),
        P("pot_18", (508, 676, 16, 16), "Corridor", sprite="pot"),
        P("carpet",(160,780,324,404),"Queens Room", color=(132,37,197),solid= False),
        P("wardrobe",(8,980,72,284),"Queens Room"),
        P("desk_chair", (96,780,28,44),"Queens Room"),
        P("bed",(304,900,276,164),"Queens Room",),
        P("nightstand", (504,820,76,80),"Queens Room"),
        P("lamp_1",(524, 740, 44,44),"Queens Room"),
        P("lamp_2",(524, 1182, 44,44),"Queens Room"),
        P("vanity_chair",(276,1182,44,28),"Queens Room"),

    ]