from utils.object_pool import ObjectPool


class MockEntity:
    def __init__(self):
        self.alive = False


def test_object_pool_acquire_and_release():
    pool = ObjectPool(MockEntity, initial=3)
    obj = pool.acquire()
    assert obj is not None
    pool.release(obj)
    assert obj in pool._free


def test_object_pool_reuse():
    pool = ObjectPool(MockEntity, initial=1)
    obj1 = pool.acquire()
    pool.release(obj1)
    obj2 = pool.acquire()
    assert obj1 is obj2


def test_object_pool_creates_new_when_empty():
    pool = ObjectPool(MockEntity, initial=0)
    obj = pool.acquire()
    assert obj is not None