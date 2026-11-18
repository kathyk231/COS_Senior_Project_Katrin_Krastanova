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

    def _find_object(self, action):
        oid =action.data.get("object")
        if not oid:
            return None
        return next((o for o in self.castle.interactable if o.id == oid ), None)

    def __call__(self, action):
        kind = action.data.get("kind", "use")
        if self.current is not action:
            self.current, self.phase, self.timer, self.last_path = action, "walk", 0.0, -1.0

            if kind =="move":
                target = self.anchors.get(action.data["goto_room"])
            else:
                obj = self._object(action)
                target = self.grid.stand_point(obj) if obj else None
            if target is None:
                return self._fail()
            self.walker.go_to(target)
        if self.phase == "walk":
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
        if self.phase =="do":
            obj = self._object(action)
            if kind =="give":
                msg = obj.on_give(self.character, obj, self.castle, item=action.data.get("item"))
            else:
                msg = obj.search(self.character, self.castle)
            print(f"[{self.character.name}] {msg}")
            self.phase = "wait"
            self.timer = 0.0
        if effects_met(self.character.facts(), action.effects):
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