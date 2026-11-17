import pygame
import textwrap
from player import Player
from player_state import PlayerState, Role
from ui import MessageLog,QuestLog
from quests import QuestManager
from servant_quests import create_servant_quests
from royal_quests import create_royal_quests
from confession import decision_cup, offer_cup
from character import Character
from world_setup import create_world
from world_actions import build_world_actions
from ai_controller import make_ai

WIDTH, HEIGHT, FPS = 960, 540, 60
SPEEDS = [1,3,8]
ROLE = Role.ROYAL
AI_ROLE = Role.SERVANT
def quests_for(role):
    return create_servant_quests()if role == Role.SERVANT else create_royal_quests()

def main():
    pygame.init()
    font = pygame.font.SysFont("Times New Roman", 20)
    big_font = pygame.font.SysFont("Times New Roman", 44)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("I will decide on a name, I promise")
    clock = pygame.time.Clock()
    screen.fill((30, 35, 50))
    loading = font.render("Building the castle...", True, (0,0,0))
    screen.blit(loading, loading.get_rect(center=(WIDTH//2,HEIGHT//2)))
    pygame.display.flip()
    messages = MessageLog(font)
    quest_log = QuestLog(font)
    castle, navmesh, grid, anchors = create_world(with_standin=Role.SERVANT in (ROLE, AI_ROLE))

    player = Player((1068, 1960), PlayerState(ROLE))
    ai = Character(f"{AI_ROLE.value.capitalize()} AI", (1068, 1960), PlayerState(AI_ROLE))
    ai.color= (60,160,90)
    characters = [player,ai]

    quests =QuestManager(quests_for(ROLE))
    quests.on_complete = lambda q: messages.say(f"Quest completed: {q.title}")
    ai_ctrl = make_ai(ai,castle,anchors,grid, build_world_actions(castle,anchors), quests_for(AI_ROLE))
    speed_i = 0
    follow_ai = True
    show_grid = False
    running = True


    while running:
        dt = min(clock.tick(FPS)/1000.0, 0.05)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue
            if event.type != pygame.KEYDOWN:
                continue
            key = event.key
            if key == pygame.K_ESCAPE:
                running = False
            elif castle.result:
                continue
            elif key == pygame.K_e:
                text = castle.interact(player)
                if text:
                    messages.say(text)
            elif key == pygame.K_b:
                messages.say(castle.give(player))
            elif castle.pending_cup and key in (pygame.K_y, pygame.K_n):
                p = castle.pending_cup
                messages.say(decision_cup(p["giver"], p["royal"], castle, key == pygame.K_y))
            elif key == pygame.K_F1:
                for o in castle.interactable:
                    if o.id == "royal_npc":
                        o.data["character"].set_flag("announce_king_death")
                        messages.say("DEBUG: announced the death")
            elif key == pygame.K_F2 and Role.ROYAL:
                fake = Character("Servant", (0,0), PlayerState(Role.SERVANT))
                fake.inventory.add_item("spiked_wine")
                messages.say(offer_cup(fake, player, castle))
            elif key == pygame.K_F3:
                show_grid = not show_grid
            elif key == pygame.K_F4:
                follow_ai = not follow_ai
            elif key == pygame.K_F5:
                speed_i = (speed_i + 1) % len(SPEEDS)

        for _ in range(SPEEDS[speed_i]):
            if not castle.result:
                player.update(dt, navmesh)
                ai_ctrl.update(dt, navmesh)
            text = castle.update(dt)
            if text:
                messages.say(text)
            navmesh.update_doors(dt, [(c.position, c.radius) for c in characters])
            for c in characters:
                c.update_room(castle)
        messages.update(dt)
        quests.update(player)
        focus = ai.position if follow_ai else player.position
        camera = pygame.Vector2(focus.x - WIDTH/2, focus.y - HEIGHT/2)
        screen.fill((30,35,50))
        castle.draw_rooms(screen, camera)
        navmesh.draw(screen, camera)
        castle.draw_prop(screen, camera)
        castle.draw_interactable(screen, camera)
        castle.draw_doors(screen, camera)
        for c in characters:
            c.draw(screen, camera)
        if show_grid:
            c = grid.cell
            for cx in range(int(camera.x // c), int(camera.x + WIDTH) + 1):
                for cy in range(int(camera.y // c), int(camera.y + HEIGHT) + 1):
                    px, py = grid.center(cx, cy)
                    pos = (int(px-camera.x),int(py-camera.y))
                    if (cx,cy)in grid.free:
                        pygame.draw.circle(screen,(0,160,0),pos,2)
                    elif (cx,cy) in grid.gates:
                        pygame.draw.circle(screen, (255,140,0),pos,3)
            if ai_ctrl.walker.points:
                pts = [ai.position] + ai_ctrl.walker.points
                pygame.draw.lines(screen, (0, 0, 0), False, [(p.x - camera.x, p.y - camera.y) for p in pts], 3)

        hud = (f"{player.state.role.value.upper()} | Room: {player.room} |Position: {int(player.position.x)}/{int(player.position.y)} | Items: {','.join(player.inventory.names()) or '-'}" + (f"| Speed x{SPEEDS[speed_i]}" if SPEEDS[speed_i] > 1 else ""))
        screen.blit(font.render(hud,True,(0,0,0)),(10,10))
        quest_log.draw(screen,quests, player)
        screen.blit(font.render(ai_ctrl.status_text(),True,(0,0,0)),(10,100))
        if castle.coronation:
            t = font.render(f"Coronation: {castle.coronation['left']:.0f}s",True,(0,0,0))
            screen.blit(t,(WIDTH//2 - t.get_width()//2,40))
        obj = castle.nearest_interactable(player)
        if obj:
            message = font.render(f"Click E:{obj.verb} {obj.name} "+("   B: Give" if obj.on_give else ""), True, (0,0,0))
            screen.blit(message,(WIDTH//2 - message.get_width()//2,HEIGHT-120))
        messages.draw(screen)
        if castle.pending_cup:
            t = font.render("A servant offers you a cup of wine!  Y: Drink   N: Refuse", True, (255,255,120))
            r = t.get_rect(center=(WIDTH//2,HEIGHT//2-120))
            pygame.draw.rect(screen,(0,0,0),r.inflate(24,12))
            screen.blit(t,r)
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
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()


