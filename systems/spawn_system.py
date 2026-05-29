import random
import math
from entities.enemy import Enemy


class SpawnSystem:
    def __init__(self, game, pool, wave_manager):
        self.game = game
        self.pool = pool
        self.wave_manager = wave_manager

    def update(self, dt):
        self.wave_manager.update(dt)

    def spawn_enemy(self, kind='normal'):
        player = self.game.player
        screen_w = self.game.width
        screen_h = self.game.height
        angle = random.random() * math.tau
        diag = math.hypot(screen_w, screen_h)
        radius = diag / 2 + 100
        wx = player.position[0] + math.cos(angle) * radius
        wy = player.position[1] + math.sin(angle) * radius
        wx = max(0, min(wx, self.game.world_size[0]))
        wy = max(0, min(wy, self.game.world_size[1]))
        enemy = self.pool.acquire()
        enemy.reset((wx, wy), kind)
        self.wave_manager.on_enemy_spawned()
        return enemy
