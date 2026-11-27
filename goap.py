import heapq
import time
import itertools

def satisfied(state,conditions):
    for k, v in conditions.items():
        have = state.get(k)
        if isinstance(v, bool):
            if bool(have) != v:
                return False
        elif have != v:
            return False
    return True
def state_key(state):
    return frozenset(state.items())
class Goal:
    def __init__(self, name, options, priority=1, essential=False):
        self.name = name
        self.options = [options] if isinstance(options, dict) else list(options)
        self.priority = priority
        self.essential = essential

    def value(self, state):
        return self.priority(state) if callable(self.priority) else self.priority
    def is_satisfied(self, state):
        return any(satisfied(state, o) for o in self.options)
    @staticmethod
    def from_step(step, priority=1):
        return Goal(step.text, step.options, priority, getattr(step, "essential", False))

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
        self.goal_cooldowns ={}
        self.last_said = None
        self.fail_streak = {}
        self.give_up=3
        self.on_stuck = None
        self.clock = None
        self.quiet = False
        self.stats = {"replans": 0, "no_plan": 0, "action_failures": 0, "actions_done": 0, "steps_skipped": 0,
                      "plan_seconds": 0.0}
    def say(self, text):
        if self.quiet:
            return
        stamp =f"{self.clock():5.0f}s " if self.clock else ""
        entry = f"{stamp}[{self.name}] {text}"
        self.log.append(entry)
        if len(self.log) >200:
            del self.log[:100]
        if entry != self.last_said:
            self.last_said = entry
            print(entry)

    def pick_goal(self, state):
        goals = self.goals() if callable(self.goals) else self.goals
        avail_goals = [g for g in goals if
                       not g.is_satisfied(state) and g.value(state) > 0 >= self.goal_cooldowns.get(g.name, 0)]
        if not avail_goals:
            return None
        return max(avail_goals, key=lambda g: g.value(state))
    def replan(self, state, goal):
        usable = [a for a in self.actions if self.cooldowns.get(a.name,0) <= 0]
        t0 = time.perf_counter()
        found = plan_any(state, goal.options, usable, role=self.role)
        self.stats["plan_seconds"] += time.perf_counter() - t0
        if time.perf_counter() - t0 > 0.1:
            print(f"slow plan {time.perf_counter() - t0:.2f} seconds for '{goal.name}'")
        self.stats["replans"] +=1
        self.goal = goal
        self.plan = found or []
        if found:
            self.fail_streak.pop(goal.name, None)
            self.say(f"goal '{goal.name}': " + " > ".join(a.name for a in self.plan))
        else:
            self.say(f"goal '{goal.name}': no plan found.")
            self.stats["no_plan"] += 1
            n = self.fail_streak.get(goal.name,0) +1
            self.fail_streak[goal.name] = n
            cap = 3 if goal.essential else 12
            self.goal_cooldowns[goal.name] = self.cooldown_steps * min(2**(n-1), cap)
            if n >= self.give_up and self.on_stuck and not goal.essential:
                self.fail_streak.pop(goal.name)
                self.on_stuck(goal)
    def step(self, state, execute):
        for table in (self.cooldowns, self.goal_cooldowns):
            for name in list(table):
                table[name] -= 1
        goal = self.pick_goal(state)
        if self.goal is not None and self.goal.is_satisfied(state):
            self.fail_streak.pop(self.goal.name, None)
        if goal is None:
            if self.running is None:
                self.goal, self.plan = None, []
                return None
            action = self.running
            result = execute(action)
            if result == "running":
                return action
            self.running, self.goal, self.plan = None, None, []
            if result != "retry":
                self.stats["actions_done" if result else "action_failures"] +=1
            return action
        if self.goal is None or goal.name != self.goal.name:
            self.running = None
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
        if result == "retry":
            self.plan = []
            return action
        if result:
            self.stats["actions_done"] +=1
            self.fail_streak.pop(action.name,None)
            self.plan.pop(0)
        else:
            self.say(f"{action.name} failed, replanning.")
            self.stats["action_failures"] +=1
            streak = self.fail_streak.get(action.name,0) + 1
            self.fail_streak[action.name] = streak
            self.cooldowns[action.name] = self.cooldown_steps * min(streak, 6)
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
        if self.cost < 0:
            raise ValueError(f"action '{self.name}: cost must not be negative.")
        if self.roles is not None and len(self.roles) == 0:
            raise ValueError(f"action '{self.name}: needs at least one role.")
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
def relevant_facts(goal,actions):
    relevant = set(goal)
    changed = True
    while changed:
        changed = False
        for a in actions:
            if relevant.intersection(a.effects):
                missing = set(a.preconditions) - relevant
                if missing:
                    relevant |= missing
                    changed = True
    return relevant
def project(state, relevant):
    return frozenset((k,v) for k,v in state.items() if k in relevant)

def plan(start, goal, actions,role=None, max_nodes= 20000):
    actions = [a for a in actions if a.allowed_for(role)]
    if satisfied(start,goal):
        return []
    relevant = relevant_facts(goal,actions)
    actions = [a for a in actions if relevant.intersection(a.effects)]
    tie = itertools.count()
    frontier = [(0,next(tie), start, [])]
    best = {project(start, relevant):0}
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
            key = project(new_state, relevant)
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