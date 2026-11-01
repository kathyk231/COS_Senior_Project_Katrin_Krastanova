from quest import QuestStep, Quest

def create_servant_quest_1():
    return Quest("s1","Investigate the Royal Room: ",[
        QuestStep("Find the key for the Corridor hidden in the Throne Room.",{"has_corridor_key":True}),
        QuestStep("Enter the Royal Room.",{"room":"Royal Room"}),
        QuestStep("Search the Royal Wardrobe for clues.",{"searched_royal_wardrobe":True}),
        QuestStep("Search the Royal Vanity for jewelry.",{"searched_royal_vanity":True}),
        QuestStep("Search the Royal Nightstand for clues.",{"searched_royal_nightstand":True}),
    ])