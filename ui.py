import textwrap

import pygame

class MessageLog:
    def __init__(self, font):
        self.font = font
        self.text = ""
        self.timer = 0.0

    def say(self, text, seconds = 3.0):
        self.text = text
        self.timer = max(seconds, len(text)//14)
    def update(self,dt):
        if self.timer > 0:
            self.timer -= dt
    def draw(self,surface):
        if self.timer <=0 or not self.text:
            return
        img = [self.font.render(line,True,(0,0,0)) for line in textwrap.wrap(self.text,90)]
        w = (max(i.get_width() for i in img))
        h =(sum(i.get_height() for i in img))
        box = pygame.Rect(0,0,w+24,h+12)
        box.midbottom = (surface.get_width()//2, surface.get_height()-10)
        pygame.draw.rect(surface,(240,240,240),box)
        y = box.top +6
        for im in img:
            surface.blit(im, (box.centerx - im.get_width()//2, y))
            y += im.get_height()
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