import math
import pygame


class Enemy:
    def __init__(self, pos=(0, 0)):
        self.position = list(pos)
        self.speed = 150.0
        self.radius = 14
        self.color = (200, 50, 50)
        self.hp = 10
        self.damage = 10
        self.alive = True

    def reset(self, pos):
        self.position[0] = pos[0]
        self.position[1] = pos[1]
        self.hp = 10
        self.alive = True

    def update(self, dt, target_pos):
        if not self.alive:
            return
        tx, ty = target_pos
        dx = tx - self.position[0]
        dy = ty - self.position[1]
        dist = math.hypot(dx, dy)
        if dist > 0:
            nx = dx / dist
            ny = dy / dist
            self.position[0] += nx * self.speed * dt
            self.position[1] += ny * self.speed * dt

    def draw(self, surface, camera):
        if not self.alive:
            return
        sx, sy = camera.world_to_screen(self.position)
        pygame.draw.circle(surface, self.color, (int(sx), int(sy)), self.radius)
        pygame.draw.circle(surface, (255, 255, 255), (int(sx), int(sy)), self.radius, 1)
