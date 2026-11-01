class QuestManager:
    def __init__(self,quests):
        self.quests = quests
        self.index = 0
        self.on_complete = None
    @property
    def finished(self):
        return self.index >= len(self.quests)
    @property
    def active(self):
        return None if self.finished else self.quests[self.index]
    def update(self,character):
        if self.finished:
            return
        quest = self.quests[self.index]
        quest.update(character)
        if quest.complete:
            if self.on_complete:
                self.on_complete(quest)
            self.index += 1
            self.update(character)

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