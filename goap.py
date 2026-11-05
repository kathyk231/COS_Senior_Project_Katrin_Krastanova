import heapq
import itertools

def satisfied(state,conditions):
    return all(state.get(k) == v for k, v in conditions.items())
def state_key(state):
    return frozenset(state.items())

class Action:
    def __init__(self, name, preconditions=None, effects=None, cost =1):
        self.name = name
        self.preconditions = preconditions or {}
        self.effects = effects or {}
        self.cost = cost
    def applicable(self, state):
        return satisfied(state,self.preconditions)
    def apply(self, state):
        new = dict(state)
        new.update(self.effects)
        return new
    def __repr__(self):
        return f"Action({self.name})"

def plan(start, goal, actions, max_nodes= 20000):
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
            new_cost = cost + action.cost
            key = state_key(new_state)
            if new_cost < best.get(key, float("inf")):
                best[key] = new_cost
                heapq.heappush(frontier, (new_cost, next(tie) ,new_state, steps + [action]))
    return None