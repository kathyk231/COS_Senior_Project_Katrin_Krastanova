from quests import QuestStep as S, Quest

def create_servant_quests():
    s1 =  Quest("s1","Investigate the Royal Room: ",[
        S("Find the key for the Corridor hidden in the Throne Room.",{"has_corridor_key":True}),
        S("Enter the Royal Room.",{"room":"Royal Room"}),
        S("Search the Royal Wardrobe for clues.",{"searched_royal_wardrobe":True}),
        S("Search the Royal Vanity for jewelry.",{"searched_royal_vanity":True}),
        S("Search the Royal Nightstand for clues.",{"searched_royal_nightstand":True}),
    ])
    s2 = Quest("s2","Investigate the King's Room: ",[
        S("Get past the king's guard (bribe him or get him drunk).", {"bribed_guard":True},[{"guard_drunk": True}]),
        S("Enter the King's Room.",{"room":"Kings Room"}),
        S("Examine the carpet.", {"searched_king_carpet":True},[{"missed_king_carpet": True}]),
        S("Examine the king's nightstand and the overturned cup.", {"searched_king_nightstand":True},[{"missed_king_nightstand": True}]),
        S("Examine the King's vanity.", {"searched_king_vanity":True},[{"missed_king_vanity": True}]),
        S("Search the King's wardrobe.",{"searched_king_wardrobe":True}),
        S("Find the King's ring under the bed.", {"has_kings_ring": True}, [{"missed_king_bed": True}]),
        S("Move the painting and use the secret passage.", {"found_passage":True}),
        S("Reach the Stable.", {"room": "Stable"})

    ], after= ["s1"])
    s3 = Quest("s3","At the Stable: ",[
        S("Talk to the farmer", {"talked_stable_guy":True}),
        S("Carry water to the horse trough.",{"watered_horses":True}),
        S("Fill the feeding rack with hay.",{"fed_horses":True}),
        S("Listed to what the farmer knows.",{"knows_secret_bag":True})
    ], after= ["s2"])
    s4 = Quest("s4","The Witch's House: ",[
        S("Follow the mushroom trail in the woods to the Witch's House.",{"room":"Witch House"}),
        S("Gather the needed ingredients (listen to the cauldron).",{"has_potion_bottle":True,"has_truth_berry":True,
                                                                     "has_light_essence":True, "has_tooth_leaf":True, "has_phoenix_feather":True}, [{"has_truth_serum":True}]),
        S("Brew the Truth Serum.",{"has_truth_serum":True}, [{"brewed_truth_serum": True}])

    ], after=["s3"])
    s5 = Quest("s5","The Confession: ",[
        S("Find the kitchen key somewhere in the Entrance Hall.",{"has_kitchen_key":True}),
        S("Enter the Kitchen.", {"room":"Kitchen"}),
        S("Take a wine cup from the cabinet.", {"has_wine_cup":True},[{"mixed_spiked_wine":True}]),
        S("Take a wine bottle from the barrel.", {"has_wine":True},[{"mixed_spiked_wine":True}]),
        S("Mix the truth serum and the wine on the Kitchen table", {"has_spiked_wine":True}),
        S("Bring it to the Throne Room", {"room":"Throne Room"}),
        S("Make the Royal drink the spiked wine.", {"royal_confessed": True})
    ], after=["s4"])

    return [s1,s2,s3,s4,s5]