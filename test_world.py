from goap import Action, make_moves
from player_state import Role

R, S = Role.ROYAL, Role.SERVANT

OPTIONS = [{"bribed_guard": True}, {"guard_drunk": True}]
def build_actions():
    actions= []
    actions += make_moves([("Corridor", "Royal Room"), ("Corridor", "Queens Room"),("Throne Room", "Entrance Hall")])
    actions += make_moves([("Throne Room", "Corridor")], roles={R})
    actions += make_moves([("Throne Room", "Corridor")], requires={("Throne Room", "Corridor"): {"has_corridor_key": True}}, roles={S})
    actions += make_moves([("Entrance Hall", "Kitchen")], requires= {("Entrance Hall", "Kitchen"): {"has_kitchen_key": True}})
    actions += [
        Action("dig pot", {"room": "Throne Room"}, {"has_corridor_key": True}, cost=2),
        Action("search vanity", {"room":"Royal Room"}, {"has_jewelry":True}),
        Action("search armor cupboard", {"room": "Entrance Hall"},{"has_kitchen_key": True}),
        Action("take wine", {"room": "Kitchen"}, {"has_wine": True}),
        Action("bribe guard", {"room": "Throne Room", "has_jewelry": True}, {"bribed_guard": True, "has_jewelry": False}),
        Action("give wine to guard", {"room": "Throne Room", "has_wine": True }, {"guard_drunk":True, "has_wine":False}, roles={S}),
        Action("intimidate guard", {"room":"Throne Room"}, {"bribed_guard": True}, cost=15, roles={R})

    ]
    return actions