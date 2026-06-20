class Camera:
    def __init__(self, width, height, world_width, world_height):
        self.width = width
        self.height = height
        self.world_width = world_width
        self.world_height = world_height
        self.x = 0
        self.y = 0
        self.ix = 0
        self.iy = 0

    def follow(self, target_pos):
        tx, ty = target_pos
        if self.world_width <= self.width:
            self.x = (self.world_width - self.width) / 2.0
        else:
            self.x = tx - self.width / 2.0
            self.x = max(0, min(self.x, self.world_width - self.width))
        if self.world_height <= self.height:
            self.y = (self.world_height - self.height) / 2.0
        else:
            self.y = ty - self.height / 2.0
            self.y = max(0, min(self.y, self.world_height - self.height))
        self.ix = int(self.x)
        self.iy = int(self.y)

    def world_to_screen(self, pos):
        x, y = pos
        return int(x - self.ix), int(y - self.iy)

    def screen_to_world(self, pos):
        x, y = pos
        return x + self.ix, y + self.iy
