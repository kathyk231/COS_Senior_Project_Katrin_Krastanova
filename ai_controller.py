from ai_movement import Walker
from goap import Goal, Agent, satisfied
from quests import QuestManager
from world_actions import sense_state
import pygame
import sabotage
from sabotage import MEMORY_TIME, sees
from role_sabotage import ROLE_GOALS

CHASE_REACH = 15
CONFRONT_REACH = 45
CHASE_TIMEOUT = 25.0
PURSUIT_MEMORY = 4.0
CHASE_SPEED = 1.1
SABOTAGE = {"spoil": lambda ch, obj, castle: sabotage.spoil_wine(ch, obj, castle)}

class WorldRunner:
    def __init__(self, character, walker,grid, castle, anchors, others):
        self.character = character
        self.walker = walker
        self.grid = grid
        self.castle = castle
        self.anchors = anchors
        self.forget = lambda key: None
        self.others = others
        self.current = None
        self.phase = None
        self.timer = 0.0
        self.last_path = 0.0
        self.base_speed = character.speed
        self.pursuing = None
        self.lost_at = None

    def tick(self, dt):
        self.timer += dt
    def cancel(self):
        self.phase = None
        self.current = None
        self.character.speed = self.base_speed
        self.walker.stop()
    def _fail(self, why=""):
        if why and self.current is not None:
            print(f"[{self.character.name}] {self.current.name} aborted: {why}")
        self.cancel()
        return False
    # ----------------- LOOKUPS --------------------
    def _find_object(self, action):
        oid =action.data.get("object")
        if not oid:
            return None
        return next((o for o in self.castle.interactable if o.id == oid ), None)
    def _door(self, action):
        return next((d for d in self.castle.doors if d.name == action.data.get("door")), None)
    def _opponent(self):
        for c in self.others:
            if c is not self.character and c.state.role != self.character.state.role and sees(self.character, c):
                return c
        return None
    def _chase_target(self,action):
        if action.data.get("kind") == "confront":
            opp = self._opponent()
            if opp is not None:
                self.pursuing, self.lost_at = opp, None
                return opp
            if self.pursuing is not None:
                if self.lost_at is None:
                    self.lost_at = self.timer
                if self.timer - self.lost_at < PURSUIT_MEMORY:
                    return self.pursuing
            return None
        obj = self._find_object(action)
        return obj.data.get("follows") if obj is not None else None
    #---------------- WALKING ------------------
    def _start_walk(self, action, kind):
        if self._chase_target(action) is not None:
            return True
        if kind == "move":
            target = self.anchors.get(action.data["goto_room"])
        elif kind == "lock":
            door = self._door(action)
            target = self.grid.anchor(door.position) if door else None
        else:
            obj = self._find_object(action)
            target = self.grid.stand_point(obj) if obj else None
        if target is None:
            return False
        self.walker.go_to(target)
        return True
    def walk(self, action, kind):
        chase = self._chase_target(action)
        if chase is not None:
            reach = CONFRONT_REACH if kind == "confront" else CHASE_REACH
            if self.character.position.distance_to(chase.position) < reach:
                self.walker.stop()
                self.phase = "do"
                return None
            if self.timer > CHASE_TIMEOUT:
                return self._fail("could not catch up")
            self.character.speed = self.base_speed * CHASE_SPEED
            if self.timer - self.last_path >= 0.5:
                self.last_path = self.timer
                self.walker.go_to(chase.position)
            if self.walker.status == "failed":
                return self._fail("no path to the target")
            return "running"
        if kind == "confront":
            return self._fail("lost sight of the target")
        status = self.walker.status
        if status == "failed":
            return self._fail()
        if status != "arrived":
            return "running"
        self.walker.stop()
        if kind == "move":
            self.current = None
            return True
        self.phase = "do"
        return None
    # ------------- PERFORM AN ACTION -----------
    def _perform(self, action, kind):
        data = action.data
        if kind == "confront":
            target = self._chase_target(action)
            if target is None:
                msg = "Noone there."
            else:
                msg = sabotage.confront(self.character, target, data["mode"], data["item"], self.castle)
                self.forget("opp_has_" + data["item"])
        elif kind == "lock":
            msg = sabotage.lock_door(self.character, self._door(action), self.castle)
        elif kind == "sabotage":
            msg = SABOTAGE[data["what"]](self.character, self._find_object(action), self.castle)
        elif kind == "give":
            obj = self._find_object(action)
            msg = obj.on_give(self.character, obj, self.castle, item = data.get("item"))
        else:
            obj = self._find_object(action)
            msg = obj.search(self.character, self.castle)
        print(f"[{self.character.name}] {msg}")
        self.character.speed = self.base_speed
    def __call__(self, action):
        kind = action.data.get("kind", "use")
        if self.current is not action:
            self.current, self.phase, self.timer, self.last_path = action, "walk", 0.0, -1.0
            self.pursuing = self.lost_at = None
            if not self._start_walk(action, kind):
                return self._fail()
        if self.phase =="walk":
            result = self.walk(action, kind)
            if result is not None:
                return result
        if self.phase == "do":
            self._perform(action, kind)
            self.phase = "wait"
            self.timer = 0.0
        state = sense_state(self.character,self.castle,self.others)
        if satisfied(state, action.effects):
            self.current = None
            return True
        if self.timer < action.data.get("wait", 0):
            return "running"
        return self._fail()
class AIController:
    def __init__(self, character, castle, agent, runner, walker, manager, others):
        self.character = character
        self.castle = castle
        self.agent = agent
        self.runner = runner
        self.walker = walker
        self.manager = manager
        self.others = others
        self.memory = {}
        self.alert = 0.0
    def forget(self, key):
        self.memory.pop(key, None)
    def _senses(self, dt):
        raw = sense_state(self.character,self.castle,self.others)
        seen = [k for k in raw if k.startswith("opp_")]
        for k in list(self.memory):
            self.memory[k] -= dt
            if self.memory[k] <= 0:
                del self.memory[k]
        for k in seen:
            self.memory[k] = MEMORY_TIME
        state = {k: v for k, v in raw.items() if not k.startswith("opp_")}
        state.update({k: True for k in self.memory})
        if seen:
            self.alert = min(10.0, self.alert + dt *0.5)
        else:
            self.alert = max(0.0, self.alert - dt *0.02)
        state["alert"]= max(self.alert, min(4.0, self.castle.time/90.0))
        return state
    def update(self, dt, navmesh):
        self.runner.tick(dt)
        if self.agent.step(self._senses(dt), self.runner) is None:
            self.runner.cancel()
        self.walker.update(dt, navmesh)
    def status_text(self):
        parts = [f"{q.title} ({q.current +1}/{len(q.steps)}): {q.current_text()}" for q in self.manager.active()]
        quest = "| ".join(parts) if parts else "all quests are completed."
        sees_text = ",".join(sorted(k[4:] for k in self.memory)) or "-"
        return f"{self.character.name} [alert {self.alert:.1f}, sees {sees_text}]: {quest}"
def make_ai(character, castle, anchors, grid, actions, quests, others):
    walker = Walker(character, grid)
    runner = WorldRunner(character, walker,grid, castle, anchors, others)
    manager = QuestManager(quests)
    extra = ROLE_GOALS.get(character.state.role)

    def goals():
        manager.update(character)
        found = [Goal.from_step(q.steps[q.current]) for q in manager.active()]
        if extra:
            found += extra()
        return found
    agent = Agent(character.name, actions, goals, role = character.state.role, cooldown = 300)
    ctrl = AIController(character, castle, agent, runner, walker, manager, others)
    runner.forget = ctrl.forget
    return ctrl