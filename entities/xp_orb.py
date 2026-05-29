import pygame


class XPOrb:
    def __init__(self, pos=(0, 0), xp=10):
        self.position = list(pos)
        self.radius = 6
        self.color = (100, 220, 255)
        self.alive = False
        self.xp = xp

    def reset(self, pos, xp=10):
        self.position[0] = pos[0]
        self.position[1] = pos[1]
        self.xp = xp
        self.alive = True

    def update(self, dt, player_pos):
        if not self.alive:
            return

    def draw(self, surface, camera):
        if not self.alive:
            return
        sx, sy = camera.world_to_screen(self.position)
        sprite = getattr(self.__class__, 'sprite', None)
        if sprite:
            w = sprite.get_width()
            h = sprite.get_height()
            surface.blit(sprite, (int(sx - w // 2), int(sy - h // 2)))
        else:
            pygame.draw.circle(surface, self.color, (int(sx), int(sy)), self.radius)
            pygame.draw.circle(surface, (255, 255, 255), (int(sx), int(sy)), self.radius, 1)
