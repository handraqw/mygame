import pygame
import sys
from .fsm import StateMachine
from .camera import Camera
from .eventbus import EventBus
from entities.player import Player
from config import WORLD_WIDTH, WORLD_HEIGHT, GRID_SIZE, ARROW_SPEED, ARROW_LIFETIME
from utils.object_pool import ObjectPool
from entities.enemy import Enemy
from systems.spawn_system import SpawnSystem
from systems.wave_manager import WaveManager
from entities.xp_orb import XPOrb
import random
import os
from entities.arrow import Arrow


class MenuState:
    def __init__(self, game):
        self.game = game
        self.button_rect = pygame.Rect(0, 0, 0, 0)

    def enter(self, data=None):
        bw = 220
        bh = 50
        bx = self.game.width // 2 - bw // 2
        by = self.game.height // 2 + 20
        self.button_rect = pygame.Rect(bx, by, bw, bh)

    def exit(self):
        pass

    def update(self, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
            self.game.fsm.change(PlayingState(self.game))


class GameOverState:
    def __init__(self, game):
        self.game = game
        self.button_rect = pygame.Rect(0, 0, 0, 0)

    def enter(self, data=None):
        bw = 220
        bh = 50
        bx = self.game.width // 2 - bw // 2
        by = self.game.height // 2 + 40
        self.button_rect = pygame.Rect(bx, by, bw, bh)

    def exit(self):
        pass

    def update(self, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
            self.game.restart_game()


class PlayingState:
    def __init__(self, game):
        self.game = game

    def enter(self, data=None):
        self.game.camera.follow(self.game.player.position)

    def exit(self):
        pass

    def update(self, dt):
        self.game.update_playing(dt)


class LevelUpState:
    def __init__(self, game):
        self.game = game
        self.options = []

    def enter(self, data=None):
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
        labels = {
            'damage': '+Урон',
            'speed': '+Скорость',
            'attack_rate': 'Быстрее атака',
            'hp': '+Здоровье',
            'range': '+Дальность',
        }
        self.options = [(k, labels.get(k, k)) for k in opts]

    def exit(self):
        self.options = []

    def update(self, dt):
        keys = pygame.key.get_pressed()
        for i in range(3):
            if keys[getattr(pygame, f'K_{i+1}')]:
                choice = self.options[i][0]
                self.game.player.level_up_apply(choice)
                self.game.fsm.change(PlayingState(self.game))
                return


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
        self.wave_manager = WaveManager(self)
        self.spawn_system = SpawnSystem(self, self.enemy_pool, self.wave_manager)
        self.events.subscribe('enemy_died', self.wave_manager.on_enemy_died)
        self.xp_orb_pool = ObjectPool(XPOrb, initial=10)
        self.arrow_pool = ObjectPool(Arrow, initial=10)
        try:
            bg_path = os.path.join('assets', 'background', 'background.png')
            self.bg_img = pygame.image.load(bg_path).convert()
            self.bg_w = self.bg_img.get_width()
            self.bg_h = self.bg_img.get_height()
        except Exception:
            self.bg_img = None
            self.bg_w = 0
            self.bg_h = 0
        def load_and_scale(path, target_size=None, alpha=True):
            try:
                img = pygame.image.load(path)
                img = img.convert_alpha() if alpha else img.convert()
                if target_size:
                    img = pygame.transform.smoothscale(img, target_size)
                return img
            except Exception:
                return None

        from config import PLAYER_SPRITE_SIZE, ENEMY_SPRITE_SIZE, XP_SPRITE_SIZE

        def first_png_in(dirpath):
            try:
                for fn in os.listdir(dirpath):
                    if fn.lower().endswith('.png'):
                        return os.path.join(dirpath, fn)
            except Exception:
                return None

        Enemy.sprite = load_and_scale(first_png_in(os.path.join('assets', 'enemies')) or '', ENEMY_SPRITE_SIZE)
        XPOrb.sprite = load_and_scale(first_png_in(os.path.join('assets', 'experience')) or '', XP_SPRITE_SIZE)
        Player.sprite = load_and_scale(first_png_in(os.path.join('assets', 'player')) or '', PLAYER_SPRITE_SIZE)

        self.fsm.change(MenuState(self))

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

    def run(self):
        while self.running:
            frame_time = self.clock.tick(60) / 1000.0
            frame_time = min(frame_time, 0.25)
            self.handle_events()
            self.accumulator += frame_time
            while self.accumulator >= self.fixed_dt:
                self.update(self.fixed_dt)
                self.accumulator -= self.fixed_dt
            self.render()

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
        for e in enemies:
            e.update(dt, self.player.position)

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
            for e in enemies:
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

    def render(self):
        if isinstance(self.fsm.state, MenuState):
            self.render_menu()
            pygame.display.flip()
            return

        if getattr(self, 'bg_img', None):
            self.draw_background()
        else:
            self.screen.fill((20, 20, 20))

        self.player.draw(self.screen, self.camera)
        for e in self.enemy_pool.for_each():
            e.draw(self.screen, self.camera)
        for arr in self.arrow_pool.for_each():
            arr.draw(self.screen, self.camera)
        for orb in self.xp_orb_pool.for_each():
            orb.draw(self.screen, self.camera)

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
        lvl_s = self.font.render(f"Ур. {lvl}", True, (255, 255, 255))
        self.screen.blit(lvl_s, (bx + bar_w + 8, by))
        wave_s = self.font.render(f"Волна {self.wave_manager.wave_index}", True, (255, 255, 255))
        wave_info = self.font.render(f"{self.wave_manager.alive_enemies}/{self.wave_manager.total_enemies}", True, (255, 255, 255))
        self.screen.blit(wave_s, (bx, by + 20))
        self.screen.blit(wave_info, (bx + 92, by + 20))

        if isinstance(self.fsm.state, LevelUpState):
            state = self.fsm.state
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            self.screen.blit(overlay, (0, 0))
            title = self.font.render("Новый уровень! Выберите улучшение (1-3)", True, (255, 255, 255))
            self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 120))
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

        if isinstance(self.fsm.state, GameOverState):
            state = self.fsm.state
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            title = self.font.render("Вы погибли", True, (255, 80, 80))
            self.screen.blit(title, (self.width // 2 - title.get_width() // 2, self.height // 2 - 80))
            self.draw_button(state.button_rect, "Начать заново")
            hint = self.font.render("Enter или клик", True, (200, 200, 200))
            self.screen.blit(hint, (self.width // 2 - hint.get_width() // 2, state.button_rect.bottom + 16))

        pygame.display.flip()

    def render_menu(self):
        self.screen.fill((20, 20, 30))
        title_font = pygame.font.SysFont(None, 48)
        title = title_font.render("Арена выживания", True, (255, 255, 255))
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, self.height // 2 - 120))
        state = self.fsm.state
        self.draw_button(state.button_rect, "Начать игру")
        hint = self.font.render("WASD — движение", True, (180, 180, 180))
        self.screen.blit(hint, (self.width // 2 - hint.get_width() // 2, state.button_rect.bottom + 20))
        hint2 = self.font.render("Enter или клик — начать", True, (140, 140, 140))
        self.screen.blit(hint2, (self.width // 2 - hint2.get_width() // 2, state.button_rect.bottom + 44))

    def draw_button(self, rect, text):
        pygame.draw.rect(self.screen, (80, 80, 120), rect)
        pygame.draw.rect(self.screen, (255, 255, 255), rect, 2)
        lbl = self.font.render(text, True, (255, 255, 255))
        self.screen.blit(lbl, (rect.centerx - lbl.get_width() // 2, rect.centery - lbl.get_height() // 2))

    def draw_grid(self):
        pass

    def draw_background(self):
        if not self.bg_img:
            return
        tile_w = self.bg_w
        tile_h = self.bg_h
        off_x = self.camera.ix % tile_w
        off_y = self.camera.iy % tile_h
        start_x = -off_x
        start_y = -off_y
        x = start_x
        while x < self.width:
            y = start_y
            while y < self.height:
                self.screen.blit(self.bg_img, (x, y))
                y += tile_h
            x += tile_w
