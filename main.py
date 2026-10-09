import pygame
from player import Player
from player_state import PlayerState, Role
from castle import Castle
from Navmesh_manager import NavmeshManager

WIDTH, HEIGHT, FPS = 960, 540, 60

def main():
    pygame.init()
    font = pygame.font.SysFont("Times New Roman", 20)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("I will decide on a name, I promise")
    clock = pygame.time.Clock()
    player_state = PlayerState(Role.SERVANT)
    player = Player((800, 600), player_state)
    characters = [player]
    castle = Castle()
    navmesh = NavmeshManager()
    navmesh.bake(castle.rooms, castle.doors, castle.passage)
    running = True
    while running:
        dt = clock.tick(FPS)/1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                castle.interact(player)
        player.update(dt,navmesh)
        navmesh.update_doors(dt,[(c.position,c.radius) for c in characters])
        for c in characters:
            c.update_room(castle)
        camera = pygame.Vector2(player.position.x - WIDTH/2, player.position.y - HEIGHT/2)
        screen.fill((30,35,50))
        castle.draw_rooms(screen, camera)
        navmesh.draw(screen, camera)
        castle.draw_doors(screen, camera)
        for c in characters:
            c.draw(screen, camera)
        hud = f"{player.state.role.value.upper()} | Room: {player.room} | Items: {','.join(player.inventory.names()) or '-'}"
        screen.blit(font.render(hud,True,(255,255,255)),(10,10))
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()


