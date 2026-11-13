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

class Agent:
    def __init__(self, name, actions,goals, role=None, cooldown =20):
        self.name = name
        self.actions = actions
        self.goals = goals
        self.role = role
        self.cooldown_steps = cooldown
        self.cooldowns = {}
        self.goal = None
        self.plan = []
        self.log = []
        self.running = None
        self.wait = 0

    def say(self, text):
        self.log.append(f"[{self.name}] {text}")
        print(self.log[-1])

    def pick_goal(self, state):
        goals = self.goals() if callable(self.goals) else self.goals
        avail_goals = [g for g in goals if not g.is_satisfied(state) and g.value(state)]
        if not avail_goals:
            return None
        return max(avail_goals, key=lambda g: g.value(state))
    def replan(self, state, goal):
        usable = [a for a in self.actions if self.cooldowns.get(a.name,0) <= 0]
        found = plan_any(state, goal.options, usable, role=self.role)
        self.goal = goal
        self.plan = found or []
        if found:
            self.say(f"goal '{goal.name}': " + " > ".join(a.name for a in self.plan))
        else:
            self.wait =60
            self.say(f"goal '{goal.name}': no plan found.")
    def step(self, state, execute):
        for name in list(self.cooldowns):
            self.cooldowns[name] -= 1
        goal = self.pick_goal(state)
        if goal is None:
            if self.running is None:
                self.goal, self.plan = None, []
                return None
            action = self.running
            result = execute(action)
            if result == "running":
                return action
            self.running, self.goal, self.plan = None, None, []
            return action
        if self.goal is None or goal.name != self.goal.name:
            self.wait = 0
            self.running = None
        if self.wait >0:
            self.wait -= 1
            return None
        if self.running is None:
            if self.goal is None or goal.name != self.goal.name or not self.plan or not self.plan[0].applicable(state):
                self.replan(state, goal)
        if not self.plan:
            return None
        action = self.plan[0]
        self.running = action
        result = execute(action)
        if result == "running":
            return action
        self.running = None
        if result:
            self.plan.pop(0)
        else:
            self.say(f"{action.name} failed, replanning.")
            self.cooldowns[action.name] = self.cooldown_steps
            self.plan = []
        return action
class Action:
    def __init__(self, name, preconditions=None, effects=None, cost =1, roles= None, role_costs = None, data=None):
        self.name = name
        self.preconditions = preconditions or {}
        self.effects = effects or {}
        self.cost = cost
        self.roles = set(roles) if roles else None
        self.role_costs = role_costs or {}
        self.data = data or {}
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
            moves.append(Action(f"go {src} -> {dst}",precond,{"room":dst},cost,roles=roles, data={"goto_room":dst}))
    return moves