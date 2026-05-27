import random
import math
from entities.enemy import Enemy


class SpawnSystem:
    def __init__(self, game, pool):
        self.game = game
        self.pool = pool
        self.spawn_timer = 0.0
        self.spawn_interval = 1.0  # seconds

    def update(self, dt):
        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.spawn_timer = self.spawn_interval
            self.spawn_enemy()

    def spawn_enemy(self):
        # spawn outside of screen bounds around player
        player = self.game.player
        cam = self.game.camera
        screen_w = self.game.width
        screen_h = self.game.height
        # choose a random angle and spawn at radius slightly outside view
        angle = random.random() * math.tau
        # spawn radius: diagonal of screen / 2 + margin
        diag = math.hypot(screen_w, screen_h)
        radius = diag / 2 + 100
        wx = player.position[0] + math.cos(angle) * radius
        wy = player.position[1] + math.sin(angle) * radius
        # clamp to world bounds
        wx = max(0, min(wx, self.game.world_size[0]))
        wy = max(0, min(wy, self.game.world_size[1]))
        enemy = self.pool.acquire()
        enemy.reset((wx, wy))
