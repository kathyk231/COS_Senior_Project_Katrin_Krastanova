import pygame
import textwrap
from player import Player
from player_state import PlayerState, Role
from castle import Castle
from Navmesh_manager import NavmeshManager
from ui import MessageLog,QuestLog
from quests import QuestManager
from servant_quests import create_servant_quests
from royal_quests import create_royal_quests
from npcs import create_r_standin
from confession import decision_cup, offer_cup
from character import Character

WIDTH, HEIGHT, FPS = 960, 540, 60

def main():
    pygame.init()
    font = pygame.font.SysFont("Times New Roman", 20)
    big_font = pygame.font.SysFont("Times New Roman", 44)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("I will decide on a name, I promise")
    clock = pygame.time.Clock()
    ROLE = Role.SERVANT
    player = Player((1068, 1960), PlayerState(ROLE))
    player.inventory.add_item("spiked_wine")
    characters = [player]
    castle = Castle()
    if ROLE == Role.SERVANT:
        castle.interactable.append(create_r_standin())
    quests =QuestManager(create_servant_quests() if ROLE == Role.SERVANT else create_royal_quests())
    quest_log = QuestLog(font)
    quests.on_complete = lambda q: messages.say(f"Quest completed: {q.title}")
    messages = MessageLog(font)
    navmesh = NavmeshManager()
    solids = [o.rect for o in castle.interactable if o.solid]
    solids += [p.rect for p in castle.props if p.solid]
    navmesh.bake(castle.rooms, castle.doors, castle.passage,solids)
    running = True
    while running:
        dt = clock.tick(FPS)/1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if castle.result:
                continue
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                text = castle.interact(player)
                if text:
                    messages.say(text)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_b:
                messages.say(castle.give(player))
            elif event.type == pygame.KEYDOWN and castle.pending_cup and event.key in (pygame.K_y,pygame.K_n):
                p = castle.pending_cup
                messages.say(decision_cup(p["giver"],p["royal"], castle, event.key == pygame.K_y))
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
                for o in castle.interactable:
                    if o.id == "royal_npc":
                        o.data["character"].set_flag("announced_king_death")
                        messages.say("DEBUG: The royal has announced the Death.")
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_F2 and ROLE == Role.ROYAL:
                fake = Character("Servant", (0,0),PlayerState(Role.SERVANT))
                fake.inventory.add_item("spiked_wine")
                messages.say(offer_cup(fake, player, castle))

        if not castle.result:
            player.update(dt,navmesh)
        text = castle.update(dt)
        if text:
            messages.say(text)
        messages.update(dt)
        navmesh.update_doors(dt,[(c.position,c.radius) for c in characters])
        for c in characters:
            c.update_room(castle)
        quests.update(player)
        camera = pygame.Vector2(player.position.x - WIDTH/2, player.position.y - HEIGHT/2)
        screen.fill((30,35,50))
        castle.draw_rooms(screen, camera)
        navmesh.draw(screen, camera)
        castle.draw_prop(screen, camera)
        castle.draw_interactable(screen, camera)
        castle.draw_doors(screen, camera)
        for c in characters:
            c.draw(screen, camera)
        hud = f"{player.state.role.value.upper()} | Room: {player.room} |Position: {int(player.position.x)}/{int(player.position.y)} | Items: {','.join(player.inventory.names()) or '-'}"
        screen.blit(font.render(hud,True,(0,0,0)),(10,10))
        quest_log.draw(screen,quests, player)
        if castle.coronation:
            t = font.render(f"Coronation: {castle.coronation['left']:.0f}s",True,(0,0,0))
            screen.blit(t,(WIDTH//2 - t.get_width()//2,40))
        obj = castle.nearest_interactable(player)
        if obj:
            message = font.render(f"Click E:{obj.verb} {obj.name} "+("   B: Give" if obj.on_give else ""), True, (0,0,0))
            screen.blit(message,(WIDTH//2 - message.get_width()//2,HEIGHT-120))
        messages.draw(screen)
        if castle.result:
            shade = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
            shade.fill((0,0,0,170))
            screen.blit(shade,(0,0))
            title = big_font.render(f"{castle.result['winner'].upper()} WINS", True, (255,215,0))
            screen.blit(title, title.get_rect(center=(WIDTH//2,HEIGHT//2-20)))
            y = HEIGHT//2 +40
            for text_line in textwrap.wrap(castle.result['text'], 60):
                line = font.render(text_line, True, (255,255,255))
                screen.blit(line,line.get_rect(center=(WIDTH//2,y)))
                y += line.get_height() + 4
        if castle.pending_cup:
            t = font.render("A servant offers you a cup of wine!  Y: Drink   N: Refuse", True, (255,255,120))
            r = t.get_rect(center=(WIDTH//2,HEIGHT//2-120))
            pygame.draw.rect(screen,(0,0,0),r.inflate(24,12))
            screen.blit(t,r)
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()


