import pygame
import random


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