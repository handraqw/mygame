class ObjectPool:
    def __init__(self, cls, initial=0, *args, **kwargs):
        self.cls = cls
        self.args = args
        self.kwargs = kwargs
        self._free = []
        self._in_use = []
        for _ in range(initial):
            self._free.append(self._create())

    def _create(self):
        return self.cls(*self.args, **self.kwargs)

    def acquire(self):
        if self._free:
            obj = self._free.pop()
        else:
            obj = self._create()
        self._in_use.append(obj)
        return obj

    def release(self, obj):
        try:
            self._in_use.remove(obj)
        except ValueError:
            pass
        self._free.append(obj)

    def for_each(self):
        return list(self._in_use)
