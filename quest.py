
class QuestStep:
    def __init__(self,text, required):
        self.text = text
        self.required = required
    def is_done(self,character):
        facts = character.facts()
        return all(facts.get(key)== value for key, value in self.required.items())
class Quest:
    def __init__(self,id,title, steps):
        self.id = id
        self.title = title
        self.steps = steps
        self.current=0
    @property
    def complete(self):
        return self.current >= len(self.steps)
    def update(self,character):
        while not self.complete and self.steps[self.current].is_done(character):
            self.current +=1
    def current_text(self):
        return "Done!" if self.complete else self.steps[self.current].text