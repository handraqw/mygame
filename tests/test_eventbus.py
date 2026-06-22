from core.eventbus import EventBus


def test_eventbus_subscribe_and_emit():
    bus = EventBus()
    results = []
    bus.subscribe('test', lambda v: results.append(v))
    bus.emit('test', 42)
    assert 42 in results


def test_eventbus_handler_exception_isolation():
    bus = EventBus()
    results = []
    bus.subscribe('test', lambda v: (_ for _ in ()).throw(ValueError("error")))
    bus.subscribe('test', lambda v: results.append(v))
    bus.emit('test', 42)
    assert 42 in results