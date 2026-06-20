import math
import pygame


class Enemy:
    def __init__(self, pos=(0, 0), kind='normal'):
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
        self.max_hp = self.hp
        self.kind = 'normal'
        self.apply_kind(kind)

    def apply_kind(self, kind):
        kinds = {
            'normal': {
                'radius': 14,
                'max_speed': 175.0,
                'max_force': 480.0,
                'arrive_radius': 72.0,
                'hp': 14,
                'xp_reward': 10,
                'damage': 12,
                'color': (200, 50, 50)
            },
            'fast': {
                'radius': 12,
                'max_speed': 265.0,
                'max_force': 580.0,
                'arrive_radius': 88.0,
                'hp': 9,
                'xp_reward': 14,
                'damage': 10,
                'color': (220, 150, 50)
            },
            'tank': {
                'radius': 18,
                'max_speed': 120.0,
                'max_force': 380.0,
                'arrive_radius': 64.0,
                'hp': 32,
                'xp_reward': 22,
                'damage': 22,
                'color': (150, 70, 200)
            }
        }
        data = kinds.get(kind, kinds['normal'])
        self.kind = kind if kind in kinds else 'normal'
        self.radius = data['radius']
        self.max_speed = data['max_speed']
        self.max_force = data['max_force']
        self.arrive_radius = data['arrive_radius']
        self.hp = data['hp']
        self.max_hp = data['hp']
        self.xp_reward = data['xp_reward']
        self.damage = data['damage']
        self.color = data['color']

    def reset(self, pos, kind='normal'):
        self.position[0] = pos[0]
        self.position[1] = pos[1]
        self.velocity[0] = 0.0
        self.velocity[1] = 0.0
        self.apply_kind(kind)
        self.alive = True

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
        sprite = getattr(self.__class__, 'sprite', None)
        if sprite:
            w = sprite.get_width()
            h = sprite.get_height()
            surface.blit(sprite, (int(sx - w // 2), int(sy - h // 2)))
        else:
            pygame.draw.circle(surface, self.color, (int(sx), int(sy)), self.radius)
            pygame.draw.circle(surface, (255, 255, 255), (int(sx), int(sy)), self.radius, 1)
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
