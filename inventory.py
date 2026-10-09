

class Inventory:
    def __init__(self):
        self.items = {}
    def add_item(self, item, amount =1):
        self.items[item] = self.items.get(item, 0) + amount
    def has(self, item, amount=1):
        return self.items.get(item, 0) >= amount
    def remove_item(self, item, amount=-1):
        if not self.has(item, amount):
            return False
        self.items[item] -= amount
        if self.items[item] == 0:
            del self.items[item]
        return True
    def count(self,item):
        return self.items.get(item, 0)
    def names(self):
        return list(self.items.keys())
    def __repr__(self):
        return f"Inventory({self.items})"