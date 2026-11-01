import pygame

class MessageLog:
    def __init__(self, font):
        self.font = font
        self.text = ""
        self.timer = 0.0

    def say(self, text, seconds = 3.0):
        self.text = text
        self.timer = seconds
    def update(self,dt):
        if self.timer > 0:
            self.timer -= dt
    def draw(self,surface):
        if self.timer <=0 or not self.text:
            return
        img = self.font.render(self.text,True,(0,0,0))
        box = img.get_rect(center = (surface.get_width()//2,surface.get_height()-25))
        pygame.draw.rect(surface,(255,255,255),box.inflate(24,12))
        surface.blit(img,box)
class QuestLog:
    def __init__(self,font):
        self.font = font
    def draw(self,surface, manager, character):
        done = sum(q.complete for q in manager.quests)
        if manager.finished:
            lines = ["All quests are completed!"]
        else:
            lines = [f"Quest {done}/{len(manager.quests)}: complete"]
            for q in manager.active():
                lines.append(f"{q.title} ({q.current +1}/{len(q.steps)}):")
                lines.append(f"~  {q.current_text()}")
        y = 40
        for line in lines:
            surface.blit(self.font.render(line,True,(0,0,0)), (10,y))
            y +=22