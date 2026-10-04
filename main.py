import pygame
from player import Player
from player_state import PlayerState, Role
from castle import Castle
from Navmesh_manager import NavmeshManager

WIDTH, HEIGHT, FPS = 960, 540, 60

def main():
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("I will decide on a name, I promise")
    clock = pygame.time.Clock()
    player_state = PlayerState(Role.ROYAL)
    player = Player((600, 350), player_state)
    castle = Castle()
    navmesh = NavmeshManager()
    navmesh.bake(castle.rooms)
    running = True
    while running:
        dt = clock.tick(FPS)/1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        player.update(dt,navmesh)
        camera = pygame.Vector2(player.position.x - WIDTH/2, player.position.y - HEIGHT/2)
        screen.fill((30,35,50))
        castle.draw(screen, camera)
        navmesh.draw(screen, camera)
        player.draw(screen, camera)
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()

