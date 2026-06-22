from core.spatial_grid import SpatialGrid


class MockObject:
    def __init__(self, pos, alive=True):
        self.position = list(pos)
        self.alive = alive


def test_spatial_grid_build():
    grid = SpatialGrid(96)
    grid.build([MockObject((100, 100)), MockObject((200, 200))])
    assert len(grid.cells) > 0


def test_spatial_grid_query_near():
    grid = SpatialGrid(96)
    obj1 = MockObject((100, 100))
    obj2 = MockObject((150, 100))
    obj3 = MockObject((500, 500))
    grid.build([obj1, obj2, obj3])
    
    result = grid.query_near((100, 100))
    assert obj1 in result
    assert obj2 in result


def test_spatial_grid_ignores_dead_objects():
    grid = SpatialGrid(96)
    obj1 = MockObject((100, 100), alive=True)
    obj2 = MockObject((150, 100), alive=False)
    grid.build([obj1, obj2])
    
    result = grid.query_near((100, 100))
    assert obj1 in result
    assert obj2 not in result