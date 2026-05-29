from bisect import bisect_left
from enum import Enum, auto
import random
from config import WAVE_PREPARE_TIME, WAVE_BASE_ENEMIES, WAVE_ENEMIES_PER_WAVE, WAVE_BASE_SPAWN_INTERVAL, WAVE_MIN_SPAWN_INTERVAL, WAVE_SPAWN_INTERVAL_DECAY, WAVE_FAST_UNLOCK, WAVE_TANK_UNLOCK


class WaveState(Enum):
    PREPARING = auto()
    ACTIVE = auto()


class WaveManager:
    def __init__(self, game):
        self.game = game
        self.state = WaveState.PREPARING
        self.wave_index = 0
        self.timer = WAVE_PREPARE_TIME
        self.spawn_timer = 0.0
        self.spawned = 0
        self.alive_enemies = 0
        self.total_enemies = 0
        self.spawn_interval = WAVE_BASE_SPAWN_INTERVAL

    def current_total_enemies(self):
        return WAVE_BASE_ENEMIES + (self.wave_index - 1) * WAVE_ENEMIES_PER_WAVE

    def current_spawn_interval(self):
        interval = WAVE_BASE_SPAWN_INTERVAL - (self.wave_index - 1) * WAVE_SPAWN_INTERVAL_DECAY
        return max(WAVE_MIN_SPAWN_INTERVAL, interval)

    def on_enemy_spawned(self):
        self.alive_enemies += 1

    def on_enemy_died(self, position=None, xp_reward=0):
        if self.alive_enemies > 0:
            self.alive_enemies -= 1
        if self.state == WaveState.ACTIVE and self.spawned >= self.total_enemies and self.alive_enemies == 0:
            self.start_prepare()

    def start_wave(self):
        self.wave_index += 1
        self.state = WaveState.ACTIVE
        self.spawned = 0
        self.total_enemies = self.current_total_enemies()
        self.spawn_interval = self.current_spawn_interval()
        self.spawn_timer = 0.0
        self.timer = 0.0

    def start_prepare(self):
        self.state = WaveState.PREPARING
        self.timer = WAVE_PREPARE_TIME
        self.spawn_timer = 0.0

    def weights_for_wave(self):
        normal = max(35, 100 - self.wave_index * 8)
        fast = 0 if self.wave_index < WAVE_FAST_UNLOCK else 20 + self.wave_index * 4
        tank = 0 if self.wave_index < WAVE_TANK_UNLOCK else 8 + self.wave_index * 3
        return [normal, fast, tank]

    def choose_enemy_kind(self):
        kinds = ['normal', 'fast', 'tank']
        weights = self.weights_for_wave()
        cumulative = []
        total = 0
        for weight in weights:
            total += weight
            cumulative.append(total)
        if total <= 0:
            return 'normal'
        roll = random.random() * total
        index = bisect_left(cumulative, roll)
        return kinds[min(index, len(kinds) - 1)]

    def update(self, dt):
        if self.state == WaveState.PREPARING:
            self.timer -= dt
            if self.timer <= 0:
                self.start_wave()
            return
        self.spawn_timer -= dt
        while self.spawned < self.total_enemies and self.spawn_timer <= 0:
            self.game.spawn_system.spawn_enemy(self.choose_enemy_kind())
            self.spawned += 1
            self.spawn_timer += self.spawn_interval
        if self.spawned >= self.total_enemies and self.alive_enemies == 0:
            self.start_prepare()