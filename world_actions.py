import pygame
from goap import Action
from player_state import Role

ROLES = list(Role)

def world_facts(castle):
    facts = {}
    if any(d.name.startswith("Hidden Passage") and not d.hidden for d in castle.doors):
        facts["passage_revealed"] = True
    return facts

def door_options(door, role):
    if role in door.allowed_role:
        return [("role", {})]
    options = []
    if door.key:
        options.append((f"key {door.key}", {"has_" + door.key: True}))
    for flag in door.pass_flags:
        options.append((flag, {flag: True}))
    return options
