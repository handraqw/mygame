import pygame
import sys
import os

from .fsm import StateMachine
from .camera import Camera
from .eventbus import EventBus
from .spatial_grid import SpatialGrid
from .states import MenuState, GameOverState, PlayingState, LevelUpState
from .renderer import Renderer
from .resource_loader import load_and_scale, first_png_in

from entities.player import Player
from entities.enemy import Enemy
from entities.xp_orb import XPOrb
from entities.arrow import Arrow

from config import (
    WORLD_WIDTH, WORLD_HEIGHT, ARROW_SPEED, ARROW_LIFETIME,
    PLAYER_SPRITE_SIZE, ENEMY_SPRITE_SIZE, XP_SPRITE_SIZE
)

from utils.object_pool import ObjectPool
from systems.spawn_system import SpawnSystem
from systems.wave_manager import WaveManager
from systems.particle_system import ParticleSystem
from systems.light_system import LightSystem


class Game:
    def __init__(self, width=800, height=600):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Арена выживания")
        self.clock = pygame.time.Clock()
        self.running = True
        self.fixed_dt = 1.0 / 60.0
        self.accumulator = 0.0
        self.font = pygame.font.SysFont(None, 24)

        self.fsm = StateMachine()
        self.events = EventBus()
        self.events.subscribe('enemy_died', self.spawn_xp_orb)

        self.camera = Camera(width, height, WORLD_WIDTH, WORLD_HEIGHT)
        self.world_size = (WORLD_WIDTH, WORLD_HEIGHT)

        self.player = Player((WORLD_WIDTH // 2, WORLD_HEIGHT // 2))
        self.camera.follow(self.player.position)
        
        self.enemy_pool = ObjectPool(Enemy, initial=5)
        self.enemy_grid = SpatialGrid(96)
        self.particles = ParticleSystem(300)
        self.light_system = LightSystem(width, height)
        
        self.wave_manager = WaveManager(self)
        self.spawn_system = SpawnSystem(self, self.enemy_pool, self.wave_manager)
        self.events.subscribe('enemy_died', self.wave_manager.on_enemy_died)
        self.events.subscribe('enemy_died', self.spawn_death_particles)
        
        self.xp_orb_pool = ObjectPool(XPOrb, initial=10)
        self.arrow_pool = ObjectPool(Arrow, initial=10)
        
        self._load_resources()

        self.renderer = Renderer(self)

        self.fsm.change(MenuState(self))

    def _load_resources(self):
        try:
            bg_path = os.path.join('assets', 'background', 'background.png')
            self.bg_img = pygame.image.load(bg_path).convert()
            self.bg_w = self.bg_img.get_width()
            self.bg_h = self.bg_img.get_height()
        except Exception:
            self.bg_img = None
            self.bg_w = 0
            self.bg_h = 0

        Enemy.sprite = load_and_scale(
            first_png_in(os.path.join('assets', 'enemies')) or '', 
            ENEMY_SPRITE_SIZE
        )
        XPOrb.sprite = load_and_scale(
            first_png_in(os.path.join('assets', 'experience')) or '', 
            XP_SPRITE_SIZE
        )
        Player.sprite = load_and_scale(
            first_png_in(os.path.join('assets', 'player')) or '', 
            PLAYER_SPRITE_SIZE
        )

    def restart_game(self):
        for e in list(self.enemy_pool.for_each()):
            e.alive = False
            self.enemy_pool.release(e)
        for arr in list(self.arrow_pool.for_each()):
            arr.alive = False
            self.arrow_pool.release(arr)
        for orb in list(self.xp_orb_pool.for_each()):
            orb.alive = False
            self.xp_orb_pool.release(orb)
        
        self.particles.clear()
        self.player = Player((WORLD_WIDTH // 2, WORLD_HEIGHT // 2))
        self.wave_manager.reset()
        self.camera.follow(self.player.position)
        self.fsm.change(PlayingState(self))

    def spawn_xp_orb(self, position, xp_reward):
        try:
            orb = self.xp_orb_pool.acquire()
            orb.reset(position, xp_reward)
        except Exception:
            pass

    def spawn_death_particles(self, position, xp_reward):
        self.particles.spawn(position, 14, (255, 120, 70), 150.0)

    def run(self):
        while self.running:
            frame_time = self.clock.tick(60) / 1000.0
            frame_time = min(frame_time, 0.25)
            self.handle_events()
            self.accumulator += frame_time
            
            while self.accumulator >= self.fixed_dt:
                self.update(self.fixed_dt)
                self.accumulator -= self.fixed_dt
            
            self.renderer.render()

        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if isinstance(self.fsm.state, MenuState):
                    if self.fsm.state.button_rect.collidepoint(event.pos):
                        self.fsm.change(PlayingState(self))
                elif isinstance(self.fsm.state, GameOverState):
                    if self.fsm.state.button_rect.collidepoint(event.pos):
                        self.restart_game()

    def update(self, dt):
        self.fsm.update(dt)

    def update_playing(self, dt):
        self.player.update(dt)
        px, py = self.player.position
        r = getattr(self.player, 'radius', 0)
        px = max(r, min(px, WORLD_WIDTH - r))
        py = max(r, min(py, WORLD_HEIGHT - r))
        self.player.position[0] = px
        self.player.position[1] = py
        self.camera.follow(self.player.position)
        self.spawn_system.update(dt)
        
        enemies = list(self.enemy_pool.for_each())
        self.enemy_grid.build(enemies)
        for e in enemies:
            neighbors = self.enemy_grid.query_near(e.position)
            e.update(dt, self.player.position, neighbors)
        self.enemy_grid.build(enemies)

        target = None
        best_d2 = None
        for e in self.enemy_grid.query_near(self.player.position, self.player.attack_range):
            if not e.alive:
                continue
            dx = e.position[0] - self.player.position[0]
            dy = e.position[1] - self.player.position[1]
            d2 = dx * dx + dy * dy
            if best_d2 is None or d2 < best_d2:
                best_d2 = d2
                target = e

        if target is not None and best_d2 is not None:
            if best_d2 <= (self.player.attack_range * self.player.attack_range):
                if getattr(self.player, 'attack_timer', 0) <= 0:
                    dx = target.position[0] - self.player.position[0]
                    dy = target.position[1] - self.player.position[1]
                    dist = (dx * dx + dy * dy) ** 0.5
                    if dist == 0:
                        ndx, ndy = 1.0, 0.0
                    else:
                        ndx, ndy = dx / dist, dy / dist
                    try:
                        arr = self.arrow_pool.acquire()
                        arr.reset(
                            self.player.position[:], 
                            (ndx, ndy), 
                            ARROW_SPEED, 
                            self.player.damage, 
                            ARROW_LIFETIME
                        )
                    except Exception:
                        arr = None
                    self.player.attack_timer = self.player.attack_cooldown

        for arr in list(self.arrow_pool.for_each()):
            arr.update(dt)
            if not arr.alive:
                try:
                    self.arrow_pool.release(arr)
                except Exception:
                    pass

        for arr in list(self.arrow_pool.for_each()):
            if not arr.alive:
                continue
            for e in self.enemy_grid.query_near(arr.position):
                if not e.alive:
                    continue
                dx = e.position[0] - arr.position[0]
                dy = e.position[1] - arr.position[1]
                d2 = dx * dx + dy * dy
                if d2 <= (e.radius + arr.radius) ** 2:
                    e.hp -= arr.damage
                    arr.alive = False
                    try:
                        self.arrow_pool.release(arr)
                    except Exception:
                        pass
                    if e.hp <= 0:
                        self.events.emit('enemy_died', e.position[:], e.xp_reward)
                        e.alive = False
                        self.enemy_pool.release(e)
                    break
        
        self.particles.update(dt)
        
        for orb in list(self.xp_orb_pool.for_each()):
            orb.update(dt, self.player.position)
            dx = orb.position[0] - self.player.position[0]
            dy = orb.position[1] - self.player.position[1]
            dist2 = dx * dx + dy * dy
            pickup_r = (orb.radius + self.player.radius)
            if dist2 <= pickup_r * pickup_r and orb.alive:
                self.player.add_xp(orb.xp)
                orb.alive = False
                self.xp_orb_pool.release(orb)
                if self.player.should_level_up():
                    self.fsm.change(LevelUpState(self))
                    return

        for e in enemies:
            if not e.alive:
                continue
            dx = e.position[0] - self.player.position[0]
            dy = e.position[1] - self.player.position[1]
            dist2 = dx * dx + dy * dy
            minr = (e.radius + self.player.radius)
            if dist2 <= minr * minr:
                if getattr(self.player, 'hit_timer', 0) <= 0:
                    self.player.hp -= e.damage
                    self.player.hit_timer = self.player.hit_cooldown

        if self.player.hp <= 0:
            self.fsm.change(GameOverState(self))