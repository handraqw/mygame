import math
import random
import pygame


class Particle:
    def __init__(self):
        self.position = [0.0, 0.0]
        self.velocity = [0.0, 0.0]
        self.life = 0.0
        self.max_life = 1.0
        self.radius = 2
        self.color = (255, 180, 80)
        self.alive = False

    def reset(self, position, velocity, life, radius, color):
        self.position[0] = position[0]
        self.position[1] = position[1]
        self.velocity[0] = velocity[0]
        self.velocity[1] = velocity[1]
        self.life = life
        self.max_life = life
        self.radius = radius
        self.color = color
        self.alive = True


class ParticleSystem:
    def __init__(self, max_count=250):
        self.particles = []
        for _ in range(max_count):
            self.particles.append(Particle())

    def spawn(self, position, count, color=(255, 180, 80), speed=120.0):
        for _ in range(count):
            p = self.get_free_particle()
            if p is None:
                return
            angle = random.random() * math.tau
            force = random.uniform(speed * 0.3, speed)
            vx = math.cos(angle) * force
            vy = math.sin(angle) * force
            life = random.uniform(0.25, 0.55)
            radius = random.randint(2, 4)
            p.reset(position, (vx, vy), life, radius, color)

    def get_free_particle(self):
        for p in self.particles:
            if not p.alive:
                return p
        return None

    def clear(self):
        for p in self.particles:
            p.alive = False

    def update(self, dt):
        for p in self.particles:
            if not p.alive:
                continue
            p.life -= dt
            if p.life <= 0:
                p.alive = False
                continue
            p.velocity[0] *= 0.96
            p.velocity[1] *= 0.96
            p.position[0] += p.velocity[0] * dt
            p.position[1] += p.velocity[1] * dt

    def draw(self, surface, camera):
        for p in self.particles:
            if not p.alive:
                continue
            sx, sy = camera.world_to_screen(p.position)
            alpha = max(0.0, min(1.0, p.life / p.max_life))
            color = (
                int(p.color[0] * alpha),
                int(p.color[1] * alpha),
                int(p.color[2] * alpha),
            )
            pygame.draw.circle(surface, color, (int(sx), int(sy)), p.radius)
