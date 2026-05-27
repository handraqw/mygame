import pygame
import sys
from .eventbus import EventBus
from .fsm import StateMachine
from .camera import Camera
from entities.player import Player
from config import WORLD_WIDTH, WORLD_HEIGHT, GRID_SIZE
from utils.object_pool import ObjectPool
from entities.enemy import Enemy
from systems.spawn_system import SpawnSystem


class PlayingState:
    def __init__(self, game):
        self.game = game

    def enter(self, data=None):
        pass

    def exit(self):
        pass

    def update(self, dt):
        self.game.update_playing(dt)


class Game:
    def __init__(self, width=800, height=600):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Survivor Arena: Infinite Field (core)")
        self.clock = pygame.time.Clock()
        self.running = True

        self.event_bus = EventBus()
        self.fsm = StateMachine()

        self.camera = Camera(width, height, WORLD_WIDTH, WORLD_HEIGHT)

        # world
        self.world_size = (WORLD_WIDTH, WORLD_HEIGHT)

        # entities
        self.player = Player((WORLD_WIDTH // 2, WORLD_HEIGHT // 2))
        # enemies
        self.enemy_pool = ObjectPool(Enemy, initial=5)
        self.spawn_system = SpawnSystem(self, self.enemy_pool)

        # start state
        self.fsm.change(PlayingState(self))

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self.handle_events()
            self.update(dt)
            self.render()

        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self, dt):
        self.fsm.update(dt)

    def update_playing(self, dt):
        self.player.update(dt)
        # clamp player to world bounds (keep inside world considering player radius)
        px, py = self.player.position
        r = getattr(self.player, 'radius', 0)
        px = max(r, min(px, WORLD_WIDTH - r))
        py = max(r, min(py, WORLD_HEIGHT - r))
        self.player.position[0] = px
        self.player.position[1] = py
        # update camera
        self.camera.follow(self.player.position)
        # update spawn system
        self.spawn_system.update(dt)
        # update enemies
        for e in list(self.enemy_pool.for_each()):
            e.update(dt, self.player.position)
            # simple collision: if touching player, apply damage and deactivate
            dx = e.position[0] - self.player.position[0]
            dy = e.position[1] - self.player.position[1]
            dist2 = dx * dx + dy * dy
            minr = (e.radius + self.player.radius)
            if dist2 <= minr * minr and e.alive:
                # apply damage and kill enemy
                self.player.hp -= e.damage
                e.alive = False
                self.enemy_pool.release(e)

    def render(self):
        # draw background grid
        self.screen.fill((20, 20, 20))
        self.draw_grid()

        # draw entities
        self.player.draw(self.screen, self.camera)
        # draw enemies
        for e in self.enemy_pool.for_each():
            e.draw(self.screen, self.camera)

        # HUD: (removed FPS counter)

        pygame.display.flip()

    def draw_grid(self):
        # draw a tiled grid to visualize movement
        grid_size = GRID_SIZE
        color1 = (40, 40, 40)
        color2 = (50, 50, 50)
        # compute pixel offset of camera inside a grid cell
        off_x = self.camera.ix % grid_size
        off_y = self.camera.iy % grid_size
        # draw grid starting slightly before the screen to cover edges
        start_x = -off_x
        start_y = -off_y
        x = start_x
        # draw columns and rows by stepping grid_size to avoid per-tile world->screen conversions
        while x < self.width:
            y = start_y
            # compute column index in world space for alternating colors
            col_world = (self.camera.ix + x) // grid_size
            i = int(col_world)
            while y < self.height:
                row_world = (self.camera.iy + y) // grid_size
                j = int(row_world)
                color = color1 if (i + j) % 2 == 0 else color2
                rect = pygame.Rect(x, y, grid_size, grid_size)
                pygame.draw.rect(self.screen, color, rect)
                y += grid_size
            x += grid_size
