import math
import pygame


class Enemy:
    def __init__(self, pos=(0, 0)):
        self.position = list(pos)
        self.velocity = [0.0, 0.0]
        self.max_speed = 150.0
        self.max_force = 420.0
        self.arrive_radius = 72.0
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
        self.velocity[0] = 0.0
        self.velocity[1] = 0.0
        self.hp = 10
        self.xp_reward = 10
        self.alive = True
        self.max_hp = self.hp

    @staticmethod
    def clamp_magnitude(vec, max_value):
        x, y = vec
        magnitude = math.hypot(x, y)
        if magnitude == 0 or magnitude <= max_value:
            return [x, y]
        scale = max_value / magnitude
        return [x * scale, y * scale]

    def seek(self, target_pos):
        tx, ty = target_pos
        dx = tx - self.position[0]
        dy = ty - self.position[1]
        dist = math.hypot(dx, dy)
        if dist == 0:
            return [0.0, 0.0]
        desired_x = dx / dist * self.max_speed
        desired_y = dy / dist * self.max_speed
        steer_x = desired_x - self.velocity[0]
        steer_y = desired_y - self.velocity[1]
        return self.clamp_magnitude((steer_x, steer_y), self.max_force)

    def arrive(self, target_pos, slow_radius=None):
        tx, ty = target_pos
        dx = tx - self.position[0]
        dy = ty - self.position[1]
        dist = math.hypot(dx, dy)
        if dist == 0:
            return [0.0, 0.0]
        slow_radius = slow_radius if slow_radius is not None else self.arrive_radius
        if dist < slow_radius:
            speed = self.max_speed * (dist / slow_radius)
        else:
            speed = self.max_speed
        desired_x = dx / dist * speed
        desired_y = dy / dist * speed
        steer_x = desired_x - self.velocity[0]
        steer_y = desired_y - self.velocity[1]
        return self.clamp_magnitude((steer_x, steer_y), self.max_force)

    def update(self, dt, target_pos):
        if not self.alive:
            return
        steering = self.arrive(target_pos)
        self.velocity[0] += steering[0] * dt
        self.velocity[1] += steering[1] * dt
        self.velocity = self.clamp_magnitude(self.velocity, self.max_speed)
        self.position[0] += self.velocity[0] * dt
        self.position[1] += self.velocity[1] * dt

    def draw(self, surface, camera):
        if not self.alive:
            return
        sx, sy = camera.world_to_screen(self.position)
        # if a sprite is provided on the class, draw it centered
        sprite = getattr(self.__class__, 'sprite', None)
        if sprite:
            w = sprite.get_width()
            h = sprite.get_height()
            surface.blit(sprite, (int(sx - w // 2), int(sy - h // 2)))
        else:
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
