import time
import random, itertools
from goap import Goal, Agent, Action, plan, plan_any, relevant_facts, satisfied
from player_state import Role
from test_world import build_actions, OPTIONS

R, S = Role.ROYAL, Role.SERVANT
res = []
def check(name, ok, note=""):
    res.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}: {name}  {note}")

acts = build_actions()
start = {"room": "Throne Room"}

# Check 1: Role filter, forbidden actions are never in a plan
bad = 0
n = 0
goals = [{"bribed_guard": True}, {"guard_drunk": True}, {"has_wine": True}, {"has_jewelry": True}, {"has_kitchen_key": True}, {"room": "Kitchen"}, {"room": "Royal Room"}, {"room": "Queens Room"}]
for role in (S, R):
    for g in goals:
        p = plan(start, g, acts, role=role)
        if p is None:
            continue
        n +=1
        bad += sum(1 for a in p if not a.allowed_for(role))

check("U1 no plan contains an action that the role may not use", bad == 0, f"({n} plans checked.)")

# Check 2: same goal, but different roles give different plans
ps = plan_any(start, OPTIONS, acts, role=S)
pr = plan_any(start, OPTIONS, acts, role=R)
check("U2 same goal gives different plans for the two roles", [a.name for a in ps] != [a.name for a in pr], f"servant {len(ps)} steps, royal {len(pr)} steps")

# Check 3: Cheapest plan
costs = {}
for role in (S, R):
    p = plan_any(start, OPTIONS, acts, role=role)
    costs[role] = sum(a.cost_for(role) for a in p)
ok3 = True
for role in (S, R):
    each = [sum(a.cost_for(role) for a in plan(start, o, acts, role=role)) for o in OPTIONS if plan(start, o, acts, role=role) is not None]
    ok3 = ok3 and costs[role] == min(each)
check("U3 plan_any returns the cheapest plan over the options", ok3, f"costs servant {costs[S]}, royal {costs[R]}")

# Check 4: Already satisfied
check("U4 goal already satisfied returns an empty plan", plan({"bribed_guard": True}, {"bribed_guard": True}, acts, role=S) == [])

# Check 5: Third role can be added by data only (a role label that goap.py has never seen)
G= "guard"
acts3 = [Action("walk", {"room": "A"}, {"room": "B"}, roles={G}), Action("open gate", {"room": "B"}, {"gate_open":True}, roles={G}),
         Action("climb wall", {"room": "A", "gate_open": True}, {"wall_climbed": True},cost=9, roles={S})]
p3 = plan({"room": "A"}, {"gate_open": True}, acts3, role=G)
check("U5 a third role is added by data only and gets a valid plan", p3 is not None and [a.name for a in p3] == ["walk", "open gate"], "(role label 'guard', goap.py is unchanged)")

# Check 6: Empty library
check("U6 empty action list gives no plan, no exception", plan(start, {"x": True}, [], role=S)is None)
#Check 7: unreachable goal
check("U7 unreachable goal gives no plan", plan(start, {"random": True}, acts, role=S)is None)
#Check 8: unknown role string
check("U8 role with no allowed actions gives no plan", plan(start, {"bribed_guard": True}, acts, role="wizard") is None)
#Check 9: no options to a goal
check("U9 a goal with an empty option list gives no plan", plan_any(start, [], acts, role=S)is None)

#Check 10: node limit
big = [Action(f"set f{i}", {},{f"f{i}": True}) for i in range(22)]
goal = {f"f{i}": True for i in range(22)}
t0 = time.perf_counter()
p= plan({}, goal, big, role=S, max_nodes=20000)
dt = time.perf_counter() - t0
check("U10 search that reaches the node limit returns no plan", p is None, f"(stopped after {dt*1000:.0f} ms)")

#Check 11: Relevant facts pruning
check("U11 relevance pruning ignored unrelated facts", plan({"room": "Throne Room", "clock": 5, "alert":3}, {"bribed_guard": True}, acts, role=R) is not None)

#Check 12: an agent with an always failing executor never raises and gives up on the step
stuck = []
ag = Agent("t", acts, [Goal("g",[{"random": True}])], role=S)
ag.quiet = True
ag.on_stuck = lambda g: stuck.append(g.name)
ok = True
try:
    for _ in range(3000):
        ag.step(dict(start), lambda a: False)
except Exception as e:
    ok = False
    print(e)
check("U12 impossible goal: no exception, on_stuck called", ok and len(stuck)>= 1, f"(on_stuck called {len(stuck)} times in 3000 steps)")

#Check 13: failing action goes on cooldown and an alternative is used
fails = []
names =[]
w = dict(start)
def ex(a):
    if a.name == "give wine to guard":
        fails.append(1)
        return False
    w.update(a.effects)
    names.append(a.name)
    return True
ag = Agent("t", acts, [Goal("g", OPTIONS)], role= S)
ag.quiet = True
for _ in range(80):
    ag.step(w, ex)
    if satisfied(w, {"bribed_guard": True}):
        break
check("U13 failing action is put on cooldown and the other option is used", satisfied(w, {"bribed_guard": True}) and len(fails)==1, f"(failed {len(fails)} time)")

# Check 14: No goals
ag = Agent("t", acts, lambda: [], role= S)
ag.quiet = True
check("U14 agent with no goals is idle and does not raise", ag.step(dict(start), lambda a: True)is None)

#Check 15: Invalid definitions
try:
    a = Action("bad", {}, {"x": True}, cost=-5, roles = set())
    p = plan({},{"x": True}, [a], role=S)
    check("U15 invalid action definition (negative cost, empty role set) is rejected", False, "(accepted without any message)")
except Exception as e:
    check("U15 invalid action definition is rejected", True, str(e))
print(f"\n{sum(res)} of {len(res)} checks passed")