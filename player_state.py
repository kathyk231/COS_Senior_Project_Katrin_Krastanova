from enum import Enum

class Role(Enum):
    ROYAL = "royal"
    SERVANT = "servant"

class PlayerState:
    def __init__(self, role):
        self.role = role
        self.abilities = set()
        self.attributes ={"authority": 0, "stealth": 0, "social": 0, "knowledge": 0}
        self.relationships = {}
