import pygame
from config import PLAYER_SPEED, PLAYER_RADIUS, PLAYER_HP, PLAYER_DAMAGE, PLAYER_ATTACK_COOLDOWN, PLAYER_ATTACK_RANGE, PLAYER_HIT_COOLDOWN


class Player:
    def __init__(self, pos=(0, 0), speed=None, radius=None, hp=None):
        self.position = list(pos)
        self.speed = speed if speed is not None else PLAYER_SPEED
        self.radius = radius if radius is not None else PLAYER_RADIUS
        self.color = (200, 200, 50)
        self.hp = hp if hp is not None else PLAYER_HP
        self.max_hp = self.hp
        self.damage = PLAYER_DAMAGE
        self.attack_cooldown = PLAYER_ATTACK_COOLDOWN
        self.attack_timer = 0.0
        self.attack_range = PLAYER_ATTACK_RANGE
        self.hit_cooldown = PLAYER_HIT_COOLDOWN
        self.hit_timer = 0.0
        self.xp = 0
        self.level = 1
        self.xp_to_next = lambda lvl: 100 * lvl

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
        if getattr(self, 'attack_timer', 0) > 0:
            self.attack_timer -= dt
        if getattr(self, 'hit_timer', 0) > 0:
            self.hit_timer -= dt

    def add_xp(self, amount):
        self.xp += amount

    def should_level_up(self):
        return self.xp >= self.xp_to_next(self.level)

    def level_up_apply(self, choice):
        if choice == 'damage':
            self.damage += 5
        elif choice == 'speed':
            self.speed += 40
        elif choice == 'attack_rate':
            self.attack_cooldown = max(0.05, self.attack_cooldown * 0.9)
        elif choice == 'hp':
            self.hp += 25
        elif choice == 'range':
            self.attack_range += 30
        self.xp -= self.xp_to_next(self.level)
        self.level += 1

    def draw(self, surface, camera):
        sx, sy = camera.world_to_screen(self.position)
        sprite = getattr(self.__class__, 'sprite', None)
        if sprite:
            w = sprite.get_width()
            h = sprite.get_height()
            surface.blit(sprite, (int(sx - w // 2), int(sy - h // 2)))
        else:
            pygame.draw.circle(surface, self.color, (int(sx), int(sy)), self.radius)
            pygame.draw.circle(surface, (255, 255, 255), (int(sx), int(sy)), self.radius, 1)
        bar_w = max(40, self.radius * 2)
        bar_h = 6
        bx = int(sx - bar_w // 2)
        by = int(sy + self.radius + 6)
        pygame.draw.rect(surface, (40, 40, 40), (bx, by, bar_w, bar_h))
        hp_frac = 0.0
        if getattr(self, 'max_hp', 0) > 0:
            hp_frac = max(0.0, min(1.0, self.hp / float(self.max_hp)))
        pygame.draw.rect(surface, (120, 220, 120), (bx, by, int(bar_w * hp_frac), bar_h))
        pygame.draw.rect(surface, (255, 255, 255), (bx, by, bar_w, bar_h), 1)
