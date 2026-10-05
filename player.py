import pygame

class Player:
    def __init__(self, position, state):
        self.position = pygame.Vector2(position)
        self.speed = 170
        self.radius = 7
        self.state = state

    def can_stand(self, position, navmesh):
        r = self.radius
        for ox,oy in ((0,0),(r,0),(-r,0),(0,r),(0,-r)):
            if not navmesh.is_walkable(pygame.Vector2(position.x+ox,position.y+oy)):
                return False
            return True

    def update(self, dt, navmesh):
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
        step = direction.normalize() *self.speed *dt
        new_x = pygame.Vector2(self.position.x + step.x, self.position.y)
        if self.can_stand(new_x, navmesh):
            self.position = new_x
        new_y = pygame.Vector2(self.position.x, self.position.y+step.y)
        if self.can_stand(new_y, navmesh):
            self.position = new_y
    def draw(self, surface, camera):
        screen_position = (self.position.x - camera.x, self.position.y - camera.y)
        pygame.draw.circle(surface, (165, 0, 0), (int(screen_position[0]),int(screen_position[1])), self.radius)