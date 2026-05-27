import pygame
import sys
from .eventbus import EventBus
from .fsm import StateMachine
from .camera import Camera
from entities.player import Player

WORLD_WIDTH = 5000
WORLD_HEIGHT = 5000


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
        # update camera
        self.camera.follow(self.player.position)

    def render(self):
        # draw background grid
        self.screen.fill((20, 20, 20))
        self.draw_grid()

        # draw entities
        self.player.draw(self.screen, self.camera)

        # HUD: (removed FPS counter)

        pygame.display.flip()

    def draw_grid(self):
        # draw a tiled grid to visualize movement
        grid_size = 64
        color1 = (40, 40, 40)
        color2 = (50, 50, 50)
        start_x = (self.camera.x // grid_size) * grid_size
        start_y = (self.camera.y // grid_size) * grid_size
        cols = self.width // grid_size + 2
        rows = self.height // grid_size + 2
        for i in range(cols):
            for j in range(rows):
                wx = start_x + i * grid_size
                wy = start_y + j * grid_size
                sx, sy = self.camera.world_to_screen((wx, wy))
                rect = pygame.Rect(sx, sy, grid_size, grid_size)
                color = color1 if (i + j) % 2 == 0 else color2
                pygame.draw.rect(self.screen, color, rect)
