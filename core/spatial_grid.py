class SpatialGrid:
    def __init__(self, cell_size):
        self.cell_size = cell_size
        self.cells = {}

    def clear(self):
        self.cells.clear()

    def cell_key(self, position):
        x, y = position
        return int(x // self.cell_size), int(y // self.cell_size)

    def add(self, obj):
        key = self.cell_key(obj.position)
        if key not in self.cells:
            self.cells[key] = []
        self.cells[key].append(obj)

    def build(self, objects):
        self.clear()
        for obj in objects:
            if getattr(obj, 'alive', True):
                self.add(obj)

    def query_near(self, position, radius=None):
        cx, cy = self.cell_key(position)
        if radius is None:
            cell_range = 1
        else:
            cell_range = int(radius // self.cell_size) + 1
        result = []
        for y in range(cy - cell_range, cy + cell_range + 1):
            for x in range(cx - cell_range, cx + cell_range + 1):
                result.extend(self.cells.get((x, y), []))
        return result