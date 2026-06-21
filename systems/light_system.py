import pygame

import config


class LightSystem:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.light_map = pygame.Surface((width, height))

    def draw_light(self, position, radius, color):
        x, y = position
        step = 12
        for r in range(radius, 0, -step):
            power = 1.0 - r / float(radius)
            draw_color = (
                min(255, 105 + int(color[0] * power)),
                min(255, 105 + int(color[1] * power)),
                min(255, 120 + int(color[2] * power)),
            )
            pygame.draw.circle(self.light_map, draw_color, (int(x), int(y)), r)

    def apply(self, surface, player_pos, camera, orbs):
        self.light_map.fill((105, 105, 120))

        player_screen = camera.world_to_screen(player_pos)
        self.draw_light(player_screen, config.PLAYER_LIGHT_RADIUS, (170, 170, 150))

        surface.blit(self.light_map, (0, 0), special_flags=pygame.BLEND_RGB_MULT)