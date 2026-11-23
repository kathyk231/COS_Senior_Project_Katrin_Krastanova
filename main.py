import pygame
import textwrap
from player import Player
from player_state import PlayerState, Role
from sabotage import lock_door
from ui import MessageLog,QuestLog
from quests import QuestManager
from servant_quests import create_servant_quests
from royal_quests import create_royal_quests
from confession import decision_cup, offer_cup, ANNOUNCED
from character import Character
from world_setup import create_world
from world_actions import build_world_actions, EVIDENCE
from ai_controller import make_ai
from role_sabotage import sabotage_actions
import sys
from settings import cfg


WIDTH, HEIGHT, FPS = 960, 540, 60
SPEEDS = [1,3,8]
MODES = {"ai": None, "servant": Role.SERVANT, "royal": Role.ROYAL}
mode = sys.argv[1] if len(sys.argv) > 1 else "ai"
ROLE = MODES[mode]
cfg.reset(int(sys.argv[2]) if len(sys.argv) > 2 else 0, deadline=1800.0 if ROLE else 600.0)
AI_ROLES = [Role.SERVANT, Role.ROYAL]
SPAWNS ={Role.ROYAL: (1068, 880), Role.SERVANT:(900,1500)}
COLORS = {Role.ROYAL: (170,60,160), Role.SERVANT:(60,160,90)}
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
    loading = font.render("Building the castle...", True, (255,255,255))
    screen.blit(loading, loading.get_rect(center=(WIDTH//2,HEIGHT//2)))
    pygame.display.flip()
    messages = MessageLog(font)
    quest_log = QuestLog(font)


    player = Player((1068, 1900), PlayerState(ROLE)) if ROLE else None
    ai_chars = []
    for role in AI_ROLES:
        if role == ROLE:
            continue
        ch = Character(f"{role.value.capitalize()} AI", SPAWNS[role], PlayerState(role))
        ch.color = COLORS[role]
        ai_chars.append(ch)
    characters = ([player] if player else []) + ai_chars
    royal = next((c for c in characters if c.state.role == Role.ROYAL), None)
    castle, navmesh, grid, anchors = create_world(royal)
    castle.characters = characters
    for c in characters:
        c.update_room(castle)
    actions = build_world_actions(castle, anchors) + sabotage_actions(castle)
    ctrls = [make_ai(ch,castle,anchors,grid, actions, quests_for(ch.state.role), characters) for ch in ai_chars]
    quests =QuestManager(quests_for(ROLE)) if player else None
    if quests:
        quests.on_complete = lambda q: messages.say(f"Quest completed: {q.title}")

    speed_i, watch_i = 0, 0
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
            elif key == pygame.K_F3:
                show_grid = not show_grid
            elif key == pygame.K_F4:
                watch_i +=1
            elif key == pygame.K_F9:
                speed_i = (speed_i + 1) % len(SPEEDS)
            elif castle.result:
                continue
            elif key == pygame.K_F1 and royal:
                royal.set_flag(ANNOUNCED)
                messages.say("DEBUG: announced the death")
            elif key == pygame.K_F2 and player and ROLE == Role.ROYAL:
                fake = Character("Servant", (0, 0), PlayerState(Role.SERVANT))
                fake.inventory.add_item("spiked_wine")
                messages.say(offer_cup(fake, player, castle))
            elif key == pygame.K_F5:
                for i,ctrl in enumerate(ctrls):
                    ctrl.character.position = pygame.Vector2(1000+80*i,880)
                    ctrl.runner.cancel()
                    ctrl.agent.plan, ctrl.agent.running = [], None
            elif key in (pygame.K_F6, pygame.K_F7):
                for ctrl in ctrls:
                    if ctrl.character.state.role == Role.SERVANT:
                        ctrl.character.inventory.add_item("truth_serum" if key == pygame.K_F6 else "kings_ring")
            elif key == pygame.K_F8:
                door = next(d for d in castle.doors if d.name == "Kings door")
                messages.say(lock_door(royal, door, castle))
            elif key == pygame.K_F10:
                for ctrl in ctrls:
                    if ctrl.character.state.role == Role.SERVANT:
                        ctrl.character.inventory.add_item("spiked_wine")
                        ctrl.character.inventory.add_item("corridor_key")
                        ctrl.character.inventory.add_item("kitchen_key")
                        for q in ctrl.manager.quests[:4]:
                            q.current = len(q.steps)
                        ctrl.manager.quests[4].current = 5
                        ctrl.runner.cancel()
                        ctrl.agent.plan, ctrl.agent.running = [], None
            elif key == pygame.K_F11:
                spot = next(o for o in castle.interactable if o.id == "burial_spot")
                spot.data["buried"] = list(EVIDENCE)
                if royal:
                    for item in EVIDENCE:
                        royal.set_flag("buried_" + item)
                for ctrl in ctrls:
                    ctrl.alert = max(ctrl.alert, 5.0)
            elif key == pygame.K_F12 and royal:
                door = next(d for d in castle.doors if d.name == "Kings door")
                lock_door(royal, door, castle)
                for ctrl in ctrls:
                    if ctrl.character.state.role == Role.SERVANT:
                        ctrl.character.set_flag("guard_drunk")
                        ctrl.runner.cancel()
                        ctrl.agent.plan, ctrl.agent.running = [], None
            elif player and key == pygame.K_e:
                text = castle.interact(player)
                if text:
                    messages.say(text)
            elif player and key == pygame.K_b:
                messages.say(castle.give(player))
            elif player and castle.pending_cup and key in (pygame.K_y, pygame.K_n):
                p = castle.pending_cup
                messages.say(decision_cup(p["giver"], p["royal"], castle, key == pygame.K_y))



        for _ in range(SPEEDS[speed_i]):
            if not castle.result:
                if player:
                    player.update(dt, navmesh)
                for ctrl in ctrls:
                    ctrl.update(dt, navmesh)
            if castle.result:
                break
            text = castle.update(dt)
            if text:
                messages.say(text)
            for note in castle.notices:
                messages.say(note)
            castle.notices.clear()
            navmesh.update_doors(dt, [(c.position, c.radius) for c in characters])
            for c in characters:
                c.update_room(castle)
        messages.update(dt)
        if quests:
            quests.update(player)
        focus = characters[watch_i % len(characters)]
        camera = pygame.Vector2(focus.position.x - WIDTH/2, focus.position.y - HEIGHT/2)
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
            for cx in range(int(camera.x // c), int((camera.x + WIDTH)//c) + 1):
                for cy in range(int(camera.y // c), int((camera.y + HEIGHT)//c) + 1):
                    px, py = grid.center(cx, cy)
                    pos = (int(px-camera.x),int(py-camera.y))
                    if (cx,cy)in grid.free:
                        pygame.draw.circle(screen,(0,160,0),pos,2)
                    elif (cx,cy) in grid.gates:
                        pygame.draw.circle(screen, (255,140,0),pos,3)
            for ctrl in ctrls:
                if ctrl.walker.points:
                    pts = [ctrl.character.position] + ctrl.walker.points
                    pygame.draw.lines(screen, (0, 0, 0), False, [(p.x - camera.x, p.y - camera.y) for p in pts], 3)

        hud = (f"{focus.name} | {focus.state.role.value.upper()} | Room: {focus.room} |Position: {int(focus.position.x)}/{int(focus.position.y)} | Items: {','.join(focus.inventory.names()) or '-'}" + (f"| Speed x{SPEEDS[speed_i]}" if SPEEDS[speed_i] > 1 else ""))
        screen.blit(font.render(hud,True,(0,0,0)),(10,10))
        if quests:
            quest_log.draw(screen,quests, player)
        for i,ctrl in enumerate(ctrls):
            screen.blit(font.render(ctrl.status_text(),True,(0,0,0)), (10, 100+22*i))
        if castle.coronation:
            t = font.render(f"Coronation: {castle.coronation['left']:.0f}s",True,(0,0,0))
            screen.blit(t,(WIDTH//2 - t.get_width()//2,40))
        if player:
            obj = castle.nearest_interactable(player)
            if obj:
                message = font.render(f"Click E:{obj.verb} {obj.name} "+("   B: Give" if obj.on_give else ""), True, (0,0,0))
                screen.blit(message,(WIDTH//2 - message.get_width()//2,HEIGHT-120))
        messages.draw(screen)
        if player and castle.pending_cup:
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


