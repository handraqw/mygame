from core.utils import circles_overlap


def test_circles_overlap_touching():
    assert circles_overlap([0, 0], 5, [10, 0], 5)


def test_circles_not_overlap():
    assert not circles_overlap([0, 0], 5, [20, 0], 5)


def test_circles_overlap_same_position():
    assert circles_overlap([10, 10], 5, [10, 10], 5)