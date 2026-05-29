import math
import pygame


class Arrow:
    def __init__(self, pos=(0, 0), direction=(1, 0), speed=600.0, damage=10):
        self.position = list(pos)
        self.direction = list(direction)
        self.speed = speed
        self.damage = damage
        self.radius = 4
        self.color = (220, 180, 80)
        self.alive = False
        self.life = 0.0

    def reset(self, pos, direction, speed, damage, lifetime):
        self.position[0] = pos[0]
        self.position[1] = pos[1]
        self.direction[0] = direction[0]
        self.direction[1] = direction[1]
        self.speed = speed
        self.damage = damage
        self.alive = True
        self.life = lifetime

    def update(self, dt, _player_pos=None):
        if not self.alive:
            return
        self.position[0] += self.direction[0] * self.speed * dt
        self.position[1] += self.direction[1] * self.speed * dt
        self.life -= dt
        if self.life <= 0:
            self.alive = False

    def draw(self, surface, camera):
        if not self.alive:
            return
        sx, sy = camera.world_to_screen(self.position)
        length = 18
        width = 6
        angle = math.degrees(math.atan2(self.direction[1], self.direction[0]))
        surf = pygame.Surface((length, width), pygame.SRCALPHA)
        pygame.draw.rect(surf, self.color, (0, 0, length, width))
        pygame.draw.rect(surf, (255, 255, 255), (0, 0, length, width), 1)
        rot = pygame.transform.rotate(surf, -angle)
        r = rot.get_rect(center=(int(sx), int(sy)))
        surface.blit(rot, r.topleft)
