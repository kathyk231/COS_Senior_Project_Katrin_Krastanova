import pygame
from player import Player
from player_state import PlayerState, Role
from castle import Castle
from Navmesh_manager import NavmeshManager
from ui import MessageLog,QuestLog
from quests import QuestManager
from servant_quests import create_servant_quests
from royal_quests import create_royal_quests

WIDTH, HEIGHT, FPS = 960, 540, 60

def main():
    pygame.init()
    font = pygame.font.SysFont("Times New Roman", 20)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("I will decide on a name, I promise")
    clock = pygame.time.Clock()
    ROLE = Role.SERVANT
    player = Player((1068, 2000), PlayerState(ROLE))
    characters = [player]
    castle = Castle()
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
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                text = castle.interact(player)
                if text:
                    messages.say(text)
            elif event.type == pygame.KEYDOWN and event.key in DEBUG_FLAGS:
                player.set_flag(DEBUG_FLAGS[event.key])
                messages.say("DEBUG"+ DEBUG_FLAGS[event.key])
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
        messages.draw(screen)
        hud = f"{player.state.role.value.upper()} | Room: {player.room} |Position: {int(player.position.x)}/{int(player.position.y)} | Items: {','.join(player.inventory.names()) or '-'}"
        screen.blit(font.render(hud,True,(0,0,0)),(10,10))
        quest_log.draw(screen,quests, player)
        if castle.coronation:
            t = font.render(f"Coronation: {castle.coronation['left']:.0f}s",True,(0,0,0))
            screen.blit(t,(WIDTH//2 - t.get_width()//2,40))
        obj = castle.nearest_interactable(player)
        if obj:
            message = font.render(f"Click E:{obj.verb} {obj.name} ", True, (0,0,0))
            screen.blit(message,(WIDTH//2 - message.get_width()//2,HEIGHT-60))
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    DEBUG_FLAGS = {
        pygame.K_F1: "bribed_guard",
        pygame.K_F2: "talked_stable_guy",
        pygame.K_F3: "knows_secret_bag",
        pygame.K_F4: "bribed_stable_guy",
        pygame.K_F5: "royal_confessed",

    }
    main()


