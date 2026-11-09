from goap import Goal, Agent
from player_state import Role
from test_world import build_actions, OPTIONS

def run(role, failing=()):
    world = {"room":"Throne Room"}

    def execute(action):
        if action.name in failing:
            return False
        world.update(action.effects)
        return True

    agent = Agent(f"{role.value} AI Agent", build_actions(), [Goal("get past the guard", OPTIONS)], role=role)
    for _ in range(60):
        if agent.step(world, execute) is None:
            break
    print("   final:", world, "\n")

run(Role.SERVANT)
run(Role.ROYAL)
run(Role.SERVANT, failing= {"give wine to guard"})