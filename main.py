import pygame
from player import Player
from Navmesh_manager import NavmeshManager
from test_world import get_geometry

WIDTH, HEIGHT, FPS = 960, 540, 60

def main():
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Window Test One")
    clock = pygame.time.Clock()
    vertices, polygons = (get_geometry())
    navmesh = NavmeshManager()
    navmesh.bake(vertices, polygons)
    player = Player((400, 300))
    running = True
    while running:
        dt = clock.tick(FPS)/1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        player.update(dt)
        screen.fill((30,35,50))
        player.draw(screen)
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()
