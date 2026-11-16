import pygame
from goap import plan, plan_cost
from player_state import PlayerState, Role
from character import Character
from world_setup import create_world
from world_actions import build_world_actions, sense_state

pygame.init()
pygame.display.set_mode((1,1))
castle, navmesh, grid, anchors = create_world()
actions = build_world_actions(castle, anchors)
print(len(actions), "actions generated OK")

for role in (Role.SERVANT, Role.ROYAL):
    ch = Character("test", (1068,880), PlayerState(role))
    ch.update_room(castle)
    state = sense_state(ch, castle)
    for goal in ({"has_water": True}, {"room":"Royal Room"}, {"has_corridor_key": True}):
        found = plan(state, goal, actions, role=role)
        label = f"{role.value:8} {list(goal)[0]} = {list(goal.values())[0]}"
        if found is None:
            print(label, "-> no plan")
        else:
            print(label, f"-> cost {plan_cost(found, role)}")
            for a in found:
                print("     ", a.name)
