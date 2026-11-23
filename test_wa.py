import pygame
from goap import plan, plan_cost, plan_any
from player_state import PlayerState, Role
from character import Character
from royal_quests import create_royal_quests
from servant_quests import create_servant_quests
from world_setup import create_world
from world_actions import build_world_actions, sense_state

pygame.init()
pygame.display.set_mode((1,1))
castle, navmesh, grid, anchors = create_world()
actions = build_world_actions(castle, anchors)
print(len(actions), "actions generated OK")

for role, make in ((Role.SERVANT, create_servant_quests),(Role.ROYAL, create_royal_quests)):
    ch = Character("test", (1068,880), PlayerState(role))
    ch.update_room(castle)
    state = sense_state(ch, castle)
    state["room"] = "Entrance Hall"
    total, failed = 0, False
    print(f"\n==={role.value.upper()}===")
    for quest in make():
        for step in quest.steps:
            if any(all(state.get(k) == v for k,v in o.items()) for o in step.options):
                continue
            found = plan_any(state, step.options, actions, role=role)
            print(found)
            if found is None:
                print(f"NO PLAN: {quest.id} / {step.text}")
                failed = True
                break
            for a in found:
                state = a.apply(state)
            total +=plan_cost(found, role)
        if failed:
            break
    if not failed:
        print("finished all quests, total cost:", round(total, 1))