class State:
    def enter(self, data=None):
        pass

    def exit(self):
        pass

    def update(self, dt):
        pass


class StateMachine:
    def __init__(self):
        self.state = None

    def change(self, new_state, data=None):
        if self.state is not None:
            try:
                self.state.exit()
            except Exception:
                pass
        self.state = new_state
        if self.state is not None:
            try:
                self.state.enter(data)
            except Exception:
                pass

    def update(self, dt):
        if self.state is not None:
            try:
                self.state.update(dt)
            except Exception:
                pass
