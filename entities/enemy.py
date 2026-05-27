import math
import pygame


class Enemy:
    def __init__(self, pos=(0, 0)):
        self.position = list(pos)
        self.speed = 150.0
        self.radius = 14
        self.color = (200, 50, 50)
        self.hp = 10
        self.xp_reward = 10
        self.damage = 10
        self.alive = True
        # max HP for health bar
        self.max_hp = self.hp

    def reset(self, pos):
        self.position[0] = pos[0]
        self.position[1] = pos[1]
        self.hp = 10
        self.xp_reward = 10
        self.alive = True
        self.max_hp = self.hp

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
        # draw health bar under enemy
        bar_w = max(32, self.radius * 2)
        bar_h = 5
        bx = int(sx - bar_w // 2)
        by = int(sy + self.radius + 6)
        pygame.draw.rect(surface, (40, 40, 40), (bx, by, bar_w, bar_h))
        hp_frac = 0.0
        if getattr(self, 'max_hp', 0) > 0:
            hp_frac = max(0.0, min(1.0, self.hp / float(self.max_hp)))
        pygame.draw.rect(surface, (220, 100, 100), (bx, by, int(bar_w * hp_frac), bar_h))
        pygame.draw.rect(surface, (255, 255, 255), (bx, by, bar_w, bar_h), 1)
