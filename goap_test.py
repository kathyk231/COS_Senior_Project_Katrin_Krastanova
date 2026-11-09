from goap import plan_any, plan_cost
from player_state import Role
from test_world import build_actions, OPTIONS

actions = build_actions()
start = {"room":"Throne Room"}
for role in (Role.SERVANT, Role.ROYAL):
    found = plan_any(start, OPTIONS,actions, role=role)
    print(f"{role.value}: cost {plan_cost(found, role)}")
    for a in found:
        print("  ", a.name)
