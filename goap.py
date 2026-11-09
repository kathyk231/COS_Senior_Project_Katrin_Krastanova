import heapq
import itertools

def satisfied(state,conditions):
    return all(state.get(k) == v for k, v in conditions.items())
def state_key(state):
    return frozenset(state.items())
class Goal:
    def __init__(self, name, options, priority=1):
        self.name = name
        self.options = [options] if isinstance(options, dict) else list(options)
        self.priority = priority

    def value(self, state):
        return self.priority(state) if callable(self.priority) else self.priority
    def is_satisfied(self, state):
        return any(satisfied(state, o) for o in self.options)
    @staticmethod
    def from_step(step, priority=1):
        return Goal(step.text, step.options, priority)


class Action:
    def __init__(self, name, preconditions=None, effects=None, cost =1, roles= None, role_costs = None):
        self.name = name
        self.preconditions = preconditions or {}
        self.effects = effects or {}
        self.cost = cost
        self.roles = set(roles) if roles else None
        self.role_costs = role_costs or {}
    def allowed_for(self, role):
        return self.roles is None or role is None or role in self.roles
    def cost_for(self, role):
        return self.role_costs.get(role, self.cost)
    def applicable(self, state):
        return satisfied(state,self.preconditions)
    def apply(self, state):
        new = dict(state)
        new.update(self.effects)
        return new
    def __repr__(self):
        return f"Action({self.name})"

def plan(start, goal, actions,role=None, max_nodes= 20000):
    actions = [a for a in actions if a.allowed_for(role)]
    if satisfied(start,goal):
        return []
    tie = itertools.count()
    frontier = [(0,next(tie), start, [])]
    best = {state_key(start):0}
    expanded = 0
    while frontier:
        cost, _, state, steps = heapq.heappop(frontier)
        if satisfied(state, goal):
            return steps
        expanded += 1
        if expanded > max_nodes:
            return None
        for action in actions:
            if not action.applicable(state):
                continue
            new_state = action.apply(state)
            new_cost = cost + action.cost_for(role)
            key = state_key(new_state)
            if new_cost < best.get(key, float("inf")):
                best[key] = new_cost
                heapq.heappush(frontier, (new_cost, next(tie) ,new_state, steps + [action]))
    return None
def plan_cost(actions, role=None):
    return sum(a.cost_for(role) for a in actions)
def plan_any(start, options, actions, role=None):
    best = None
    for option in options:
        found = plan(start,option,actions,role=role)
        if found is not None and (best is None or plan_cost(found,role) < plan_cost(best,role)):
            best = found
    return best
def make_moves(edges, requires=None, cost =1, roles=None):
    requires = requires or {}
    moves = []
    for a, b in edges:
        extra = requires.get((a,b)) or requires.get((b,a)) or {}
        for src, dst in ((a,b), (b,a)):
            precond = {"room":src}
            precond.update(extra)
            moves.append(Action(f"go {src} -> {dst}",precond,{"room":dst},cost,roles=roles))
    return moves