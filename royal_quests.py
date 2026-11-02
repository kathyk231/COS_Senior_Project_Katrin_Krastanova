from quests import Quest, QuestStep as S

def create_royal_quests():

    r1 = Quest("r1", "Collect evidence from the Queen's Room:",[
        S("Find the Queen's Room key in the corridor.", {"has_queens_room_key": True}),
        S("Enter the Queen's Room.", {"room":"Queens Room"}),
        S("Take the letters from the desk.",{"has_letters":True}),
        S("Find the Queen's Ring.", {"has_queens_ring": True},[{"bribed_stable_guy":True}])
    ])
    r2 = Quest("r2", "Silence the King's guard:",[
        S("Go to your room.", {"room":"Royal Room"}),
        S("Take jewelry from your room.",{"has_jewelry": True},[{"bribed_guard":True}]),
        S("Take the empty bottle from your nightstand.",{"has_empty_bottle":True}),
        S("Bribe the King's guard.",{"bribed_guard":True})
    ],after=["r1"])
    r3= Quest("r3", "Clean the scene:",[
        S("Enter the King's room.",{"room":"Kings Room"}),
        S("Take the overturned cup from the nightstand.", {"has_overturned_cup": True}),
        S("Take the suspicious robe from the vanity.",{"has_suspicious_robe": True}),
        S("Take the King's ring from under the bed",{"has_kings_ring": True}),

    ],after=["r2"])
    r4= Quest("r4", "Hide evidence:",[
        S("Find the Stable key somewhere in the throne room.", {"has_stable_key": True}, [{"room":"Stable"}]),
        S("Enter the Stable.", {"room":"Stable"}),
        S("Take water from the Stable.", {"has_water": True}),
        S("Go to the King's Room again.",{"room":"Kings Room"}),
        S("Clean the carpet from the blood.", {"removed_king_carpet": True}),
        S("Go back to the Stable.", {"room":"Stable"}),
        S("Bribe the Farmer.",{"bribed_stable_guy": True}),
        S("Take a spade from the Tool Rack.",{"has_spade": True}),
        S("Go to the Woods.", {"room":"Woods"}),
        S("Find a place in the woods to bury the evidence.",{"buried_overturned_cup": True,"buried_empty_bottle":True,
                                                             "buried_suspicious_robe":True, "buried_letters":True})
    ],after=["r3"])
    r5= Quest("r5", "Take Throne:",[
        S("Go to the Throne Room.",{"room":"Throne Room"}),
        S("Announce the king's death on the podium.",{"announce_king_death": True}),
        S("Sit on the throne for 10 seconds.", {"crowned":True})
    ], after=["r4"])

    return [r1,r2,r3,r4,r5]