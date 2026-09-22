import pygame

class Player:
    def __init__(self, position):
        self.position = pygame.Vector2(position)
        self.speed = 170
        self.radius = 7

    def update(self, dt):
        keys = pygame.key.get_pressed()
        direction = pygame.Vector2(0, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            direction.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            direction.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            direction.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            direction.x += 1
        if direction.length_squared() == 0:
            return
        direction = direction.normalize()
        new_position = (self.position + direction * self.speed * dt)
        #if navmesh.is_walkable(new_position):
        self.position = new_position
    def draw(self, surface):
        pygame.draw.circle(surface, (193, 217, 150), (int(self.position.x), int(self.position.y)), self.radius)