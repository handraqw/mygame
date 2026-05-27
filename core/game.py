import pygame
import sys
# event bus not used yet; removed to avoid unused import
from .fsm import StateMachine
from .camera import Camera
from entities.player import Player
from config import WORLD_WIDTH, WORLD_HEIGHT, GRID_SIZE, ARROW_SPEED, ARROW_LIFETIME
from utils.object_pool import ObjectPool
from entities.enemy import Enemy
from systems.spawn_system import SpawnSystem
from entities.xp_orb import XPOrb
import random
from entities.arrow import Arrow


class PlayingState:
    def __init__(self, game):
        self.game = game

    def enter(self, data=None):
        pass

    def exit(self):
        pass

    def update(self, dt):
        self.game.update_playing(dt)


class LevelUpState:
    def __init__(self, game):
        self.game = game
        self.options = []

    def enter(self, data=None):
        # pick 3 unique upgrades with weights
        pool = [
            ('damage', 30),
            ('speed', 20),
            ('attack_rate', 20),
            ('hp', 20),
            ('range', 10),
        ]
        keys = [p[0] for p in pool]
        weights = [p[1] for p in pool]
        opts = []
        while len(opts) < 3:
            choice = random.choices(keys, weights=weights, k=1)[0]
            if choice not in opts:
                opts.append(choice)
        # human-friendly labels
        labels = {
            'damage': '+Damage',
            'speed': '+Speed',
            'attack_rate': 'Faster Attack',
            'hp': '+Max HP',
            'range': '+Range',
        }
        self.options = [(k, labels.get(k, k)) for k in opts]

    def exit(self):
        self.options = []

    def update(self, dt):
        # handle input: 1,2,3 to pick
        keys = pygame.key.get_pressed()
        for i in range(3):
            if keys[getattr(pygame, f'K_{i+1}')]:
                choice = self.options[i][0]
                self.game.player.level_up_apply(choice)
                # go back to playing
                self.game.fsm.change(PlayingState(self.game))
                return


class Game:
    def __init__(self, width=800, height=600):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Survivor Arena: Infinite Field (core)")
        self.clock = pygame.time.Clock()
        self.running = True
        # font for HUD
        self.font = pygame.font.SysFont(None, 24)

        self.fsm = StateMachine()

        self.camera = Camera(width, height, WORLD_WIDTH, WORLD_HEIGHT)

        # world
        self.world_size = (WORLD_WIDTH, WORLD_HEIGHT)

        # entities
        self.player = Player((WORLD_WIDTH // 2, WORLD_HEIGHT // 2))
        # enemies
        self.enemy_pool = ObjectPool(Enemy, initial=5)
        self.spawn_system = SpawnSystem(self, self.enemy_pool)
        # kills counter removed (not used in HUD)
        # xp orbs
        self.xp_orb_pool = ObjectPool(XPOrb, initial=10)
        # arrows
        self.arrow_pool = ObjectPool(Arrow, initial=10)

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
        # update enemies positions
        enemies = list(self.enemy_pool.for_each())
        for e in enemies:
            e.update(dt, self.player.position)

        # player auto-attack: find nearest enemy within range
        target = None
        best_d2 = None
        for e in enemies:
            if not e.alive:
                continue
            dx = e.position[0] - self.player.position[0]
            dy = e.position[1] - self.player.position[1]
            d2 = dx * dx + dy * dy
            if best_d2 is None or d2 < best_d2:
                best_d2 = d2
                target = e

        # shoot arrow towards target when ready
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
                        arr.reset(self.player.position[:], (ndx, ndy), ARROW_SPEED, self.player.damage, ARROW_LIFETIME)
                    except Exception:
                        arr = None
                    self.player.attack_timer = self.player.attack_cooldown

        # update arrows
        for arr in list(self.arrow_pool.for_each()):
            arr.update(dt)
            if not arr.alive:
                try:
                    self.arrow_pool.release(arr)
                except Exception:
                    pass

        # arrow collisions with enemies
        for arr in list(self.arrow_pool.for_each()):
            if not arr.alive:
                continue
            for e in enemies:
                if not e.alive:
                    continue
                dx = e.position[0] - arr.position[0]
                dy = e.position[1] - arr.position[1]
                d2 = dx * dx + dy * dy
                if d2 <= (e.radius + arr.radius) ** 2:
                    # hit
                    e.hp -= arr.damage
                    arr.alive = False
                    try:
                        self.arrow_pool.release(arr)
                    except Exception:
                        pass
                    if e.hp <= 0:
                        # spawn xp orb
                        try:
                            orb = self.xp_orb_pool.acquire()
                            orb.reset(e.position, e.xp_reward)
                        except Exception:
                            pass
                        e.alive = False
                        self.enemy_pool.release(e)
                    break
        # update xp orbs
        for orb in list(self.xp_orb_pool.for_each()):
            orb.update(dt, self.player.position)
            # pickup check
            dx = orb.position[0] - self.player.position[0]
            dy = orb.position[1] - self.player.position[1]
            dist2 = dx * dx + dy * dy
            pickup_r = (orb.radius + self.player.radius)
            if dist2 <= pickup_r * pickup_r and orb.alive:
                self.player.add_xp(orb.xp)
                orb.alive = False
                self.xp_orb_pool.release(orb)
                # check level up
                if self.player.should_level_up():
                    self.fsm.change(LevelUpState(self))
                    return

        
        # collisions (contact damage) with hit cooldown on player
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

    def render(self):
        # draw background grid
        self.screen.fill((20, 20, 20))
        self.draw_grid()

        # draw entities
        self.player.draw(self.screen, self.camera)
        # draw enemies
        for e in self.enemy_pool.for_each():
            e.draw(self.screen, self.camera)
        # draw arrows
        for arr in self.arrow_pool.for_each():
            arr.draw(self.screen, self.camera)
        # draw xp orbs
        for orb in self.xp_orb_pool.for_each():
            orb.draw(self.screen, self.camera)

        # HUD: (removed FPS counter)
        # HUD: XP bar at top
        # draw XP bar at top center
        xp = getattr(self.player, 'xp', 0)
        lvl = getattr(self.player, 'level', 1)
        xp_next = self.player.xp_to_next(lvl)
        bar_w = 300
        bar_h = 12
        bx = self.width // 2 - bar_w // 2
        by = 8
        pygame.draw.rect(self.screen, (60, 60, 60), (bx, by, bar_w, bar_h))
        fill = max(0, min(1.0, xp / xp_next))
        pygame.draw.rect(self.screen, (100, 200, 100), (bx, by, int(bar_w * fill), bar_h))
        lvl_s = self.font.render(f"Lv {lvl}", True, (255, 255, 255))
        # draw level to the right of the bar
        self.screen.blit(lvl_s, (bx + bar_w + 8, by))

        # if level up state active, draw overlay options
        if isinstance(self.fsm.state, LevelUpState):
            state = self.fsm.state
            # translucent overlay
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            self.screen.blit(overlay, (0, 0))
            title = self.font.render("Level Up! Choose an upgrade (1-3)", True, (255, 255, 255))
            self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 120))
            # draw three boxes
            box_w = 220
            box_h = 80
            start_x = self.width // 2 - (box_w * 3 + 40) // 2
            y = 200
            for i, opt in enumerate(state.options):
                x = start_x + i * (box_w + 20)
                rect = pygame.Rect(x, y, box_w, box_h)
                pygame.draw.rect(self.screen, (80, 80, 120), rect)
                pygame.draw.rect(self.screen, (255, 255, 255), rect, 2)
                lbl = self.font.render(f"{i+1}. {opt[1]}", True, (255, 255, 255))
                self.screen.blit(lbl, (x + 12, y + 24))

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
