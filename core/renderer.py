import pygame
from .states import MenuState, LevelUpState, GameOverState


class Renderer:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.width = game.width
        self.height = game.height
        self.font = game.font

    def render(self):
        if isinstance(self.game.fsm.state, MenuState):
            self.render_menu()
            pygame.display.flip()
            return

        if getattr(self.game, 'bg_img', None):
            self.draw_background()
        else:
            self.screen.fill((20, 20, 20))

        self.game.player.draw(self.screen, self.game.camera)
        for e in self.game.enemy_pool.for_each():
            e.draw(self.screen, self.game.camera)
        for arr in self.game.arrow_pool.for_each():
            arr.draw(self.screen, self.game.camera)
        for orb in self.game.xp_orb_pool.for_each():
            orb.draw(self.screen, self.game.camera)
        
        self.game.particles.draw(self.screen, self.game.camera)
        self.game.light_system.apply(
            self.screen, 
            self.game.player.position, 
            self.game.camera, 
            self.game.xp_orb_pool.for_each(), 
            self.game.player.attack_range
        )

        self.draw_hud()

        if isinstance(self.game.fsm.state, LevelUpState):
            self.draw_levelup_overlay()

        if isinstance(self.game.fsm.state, GameOverState):
            self.draw_gameover_overlay()

        pygame.display.flip()

    def draw_hud(self):
        xp = getattr(self.game.player, 'xp', 0)
        lvl = getattr(self.game.player, 'level', 1)
        xp_next = self.game.player.xp_to_next(lvl)
        bar_w = 300
        bar_h = 12
        bx = self.width // 2 - bar_w // 2
        by = 8
        
        pygame.draw.rect(self.screen, (60, 60, 60), (bx, by, bar_w, bar_h))
        fill = max(0, min(1.0, xp / xp_next))
        pygame.draw.rect(self.screen, (100, 200, 100), (bx, by, int(bar_w * fill), bar_h))
        
        lvl_s = self.font.render(f"Ур. {lvl}", True, (255, 255, 255))
        self.screen.blit(lvl_s, (bx + bar_w + 8, by))
        
        wave_s = self.font.render(f"Волна {self.game.wave_manager.wave_index}", True, (255, 255, 255))
        wave_info = self.font.render(
            f"{self.game.wave_manager.alive_enemies}/{self.game.wave_manager.total_enemies}", 
            True, 
            (255, 255, 255)
        )
        self.screen.blit(wave_s, (bx, by + 20))
        self.screen.blit(wave_info, (bx + 92, by + 20))

    def draw_levelup_overlay(self):
        state = self.game.fsm.state
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

    def draw_gameover_overlay(self):
        state = self.game.fsm.state
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        title = self.font.render("Вы погибли", True, (255, 80, 80))
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, self.height // 2 - 80))
        
        self.draw_button(state.button_rect, "Начать заново")
        
        hint = self.font.render("Enter или клик", True, (200, 200, 200))
        self.screen.blit(hint, (self.width // 2 - hint.get_width() // 2, state.button_rect.bottom + 16))

    def render_menu(self):
        self.screen.fill((20, 20, 30))
        title_font = pygame.font.SysFont(None, 48)
        title = title_font.render("Арена выживания", True, (255, 255, 255))
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, self.height // 2 - 120))
        
        state = self.game.fsm.state
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
        bg_img = getattr(self.game, 'bg_img', None)
        if not bg_img:
            return
        
        tile_w = self.game.bg_w
        tile_h = self.game.bg_h
        off_x = self.game.camera.ix % tile_w
        off_y = self.game.camera.iy % tile_h
        
        start_x = -off_x
        start_y = -off_y
        x = start_x
        
        while x < self.width:
            y = start_y
            while y < self.height:
                self.screen.blit(bg_img, (x, y))
                y += tile_h
            x += tile_w