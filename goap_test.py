from goap import Action, plan, plan_cost
from player_state import Role

R, S = Role.ROYAL, Role.SERVANT
actions = [
    Action("take jewelry", {}, {"has_jewelry":True}, cost= 3, role_costs={R:1}),
    Action("bribe guard", {"room": "Throne Room", "has_jewelry": True}, {"bribed_guard":True, "has_jewelry":False}),
    Action("enter kings room", {"room":"Throne Room"}, {"room": "Kings Room"}, roles={R}),
    Action("enter kings room (bribe)", {"room":"Throne Room", "bribed_guard":True}, {"room": "Kings Room"}, roles={S}),
    Action("examine carpet", {"room":"Kings Room"}, {"searched_king_carpet": True}, roles={S}),
    Action("scrub carpet", {"room": "Kings Room"}, {"removed_king_carpet": True}, cost=2, roles={R}),
]
start = {"room":"Throne Room"}
def show(role, goal):
    found = plan(start, goal, actions, role=role)
    if found is None:
        print(f"{role.value:8} no plan")
        return
    print(f"{role.value:8} cost {plan_cost(found, role)}: " + " > ".join(a.name for a in found))
show(S,{"searched_king_carpet":True})
show(R,{"removed_king_carpet":True})
show(S, {"removed_king_carpet": True})
show(S, {"has_jewelry":True})
show(R, {"has_jewelry":True})
