class EventBus:
    def __init__(self):
        self._listeners = {}

    def subscribe(self, event_name, callback):
        self._listeners.setdefault(event_name, []).append(callback)

    def unsubscribe(self, event_name, callback):
        lst = self._listeners.get(event_name)
        if lst and callback in lst:
            lst.remove(callback)

    def emit(self, event_name, *args, **kwargs):
        for cb in list(self._listeners.get(event_name, [])):
            try:
                cb(*args, **kwargs)
            except Exception as e:
                # swallow listener exceptions to avoid breaking game loop; could log if needed
                pass
