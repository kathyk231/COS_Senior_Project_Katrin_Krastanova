from goap import Action, plan

actions = [
    Action("dig pot", {"room": "Throne Room"}, {"has_corridor_key":True}),
    Action("go to corridor", {"room": "Throne Room","has_corridor_key":True }, {"room": "Corridor"}),
    Action("go to royal room", {"room": "Corridor"}, {"room":"Royal Room"}),
    Action("search vanity", {"room":"Royal Room"}, {"has_jewelry": True})
]
start = {"room":"Throne Room"}
print(plan(start, {"has_jewelry":True}, actions))
print(plan(start, {"room":"Throne Room"}, actions))
print(plan(start, {"has_wine":True}, actions))