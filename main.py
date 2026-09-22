import pygame

WIDTH, HEIGHT, FPS = 960, 540, 60

def main():
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Window Test One")
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill((30,35,50))
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()
