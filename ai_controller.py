from ai_movement import Walker
from goap import Goal, Agent, satisfied
from quests import QuestManager
from world_actions import sense_state
import pygame
import sabotage
from sabotage import MEMORY_TIME, sees
from role_sabotage import ROLE_GOALS

CHASE_REACH = 45
CHASE_TIMEOUT = 25.0

class WorldRunner:
    def __init__(self, character, walker,grid, castle, anchors, others):
        self.character = character
        self.walker = walker
        self.grid = grid
        self.castle = castle
        self.anchors = anchors
        self.others = others
        self.current = None
        self.phase = None
        self.timer = 0.0
        self.last_path = 0.0

    def tick(self, dt):
        self.timer += dt
    def cancel(self):
        self.phase = None
        self.current = None
        self.walker.stop()
    def _fail(self):
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
            return self._opponent()
        obj = self._find_object(action)
        return obj.data.get("follows") if obj is not None else None
    #---------------- WALKING ------------------
    def _start_walk(self, action, kind):
        if self._chase_target(action):
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
            if self.character.position.distance_to(chase.position) < CHASE_REACH:
                self.walker.stop()
                self.phase = "do"
                return None
            if self.timer > CHASE_TIMEOUT:
                return self._fail()
        if kind == "confront":
            return self._fail()
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



    def __call__(self, action):
        kind = action.data.get("kind", "use")
        if self.current is not action:
            self.current, self.phase, self.timer, self.last_path = action, "walk", 0.0, -1.0
            if not self._start_walk(action, kind):
                return self._fail()
            if self.phase =="walk":
                result = self.walk(action, kind)
                if result is not None:
                    return result
            if self.phase == "do":
                self.phase == "wait"
                self.timer = 0.0
            state = sense_state(self.character,self.castle,self.others)
            if satisfied(state, action.effects):
                self.current = None
                return True
        if self.timer < action.data.get("wait", 0):
            return "running"
        return self._fail()
class AIController:
    def __init__(self, character, castle, agent, runner, walker, manager):
        self.character = character
        self.castle = castle
        self.agent = agent
        self.runner = runner
        self.walker = walker
        self.manager = manager
    def update(self, dt, navmesh):
        self.runner.tick(dt)
        state = sense_state(self.character,self.castle)
        if self.agent.step(state, self.runner) is None:
            self.runner.cancel()
        self.walker.update(dt, navmesh)
    def status_text(self):
        parts = [f"{q.title} ({q.current +1}/{len(q.steps)}): {q.current_text()}" for q in self.manager.active()]
        return f"{self.character.name}: " + (" | ".join(parts) if parts else "all quests are completed.")
def make_ai(character, castle, anchors, grid, actions, quests):
    walker = Walker(character, grid)
    runner = WorldRunner(character, walker,grid, castle, anchors)
    manager = QuestManager(quests)

    def goals():
        manager.update(character)
        return [Goal.from_step(q.steps[q.current]) for q in manager.active()]
    agent = Agent(character.name, actions, goals, role = character.state.role, cooldown = 300)
    return AIController(character, castle, agent, runner, walker, manager)