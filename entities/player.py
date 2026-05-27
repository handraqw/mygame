import pygame


class Player:
    def __init__(self, pos=(0, 0)):
        self.position = list(pos)
        self.speed = 300.0  # units per second
        self.radius = 18
        self.color = (200, 200, 50)
        self.hp = 100

    def handle_input(self, keys, dt):
        vx = 0
        vy = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            vy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            vy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            vx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            vx += 1
        if vx != 0 or vy != 0:
            # normalize
            import math

            l = math.hypot(vx, vy)
            if l != 0:
                vx /= l
                vy /= l
            self.position[0] += vx * self.speed * dt
            self.position[1] += vy * self.speed * dt

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.handle_input(keys, dt)

    def draw(self, surface, camera):
        sx, sy = camera.world_to_screen(self.position)
        pygame.draw.circle(surface, self.color, (int(sx), int(sy)), self.radius)
        # draw bounding circle
        pygame.draw.circle(surface, (255, 255, 255), (int(sx), int(sy)), self.radius, 1)
