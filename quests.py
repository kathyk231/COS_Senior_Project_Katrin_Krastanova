class QuestManager:
    def __init__(self,quests):
        self.quests = quests
        self.on_complete = None
    @property
    def finished(self):
        return all(q.complete for q in self.quests)

    def active(self):
        done = {q.id for q in self.quests if q.complete}
        return [q for q in self.quests if not q.complete and all(a in done for a in q.after)]
    def update(self,character):
        changed = True
        while changed:
            changed = False
            for quest in self.active():
                quest.update(character)
                if quest.complete:
                    changed= True
                    if self.on_complete:
                        self.on_complete(quest)

class QuestStep:
    def __init__(self,text, required, alternatives = None):
        self.text = text
        self.required = required
        self.options = [required] + (alternatives or [])
    def is_done(self,character):
        facts = character.facts()
        return any(all(facts.get(key)== value for key, value in option.items()) for option in self.options)

class Quest:
    def __init__(self,id,title, steps, after = None):
        self.id = id
        self.title = title
        self.steps = steps
        self.after = after or []
        self.current=0
    @property
    def complete(self):
        return self.current >= len(self.steps)
    def update(self,character):
        while not self.complete and self.steps[self.current].is_done(character):
            self.current +=1
    def current_text(self):
        return "Done!" if self.complete else self.steps[self.current].text