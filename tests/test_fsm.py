from core.fsm import State, StateMachine


class MockState(State):
    def __init__(self):
        self.entered = False
        self.exited = False
    
    def enter(self, data=None):
        self.entered = True
    
    def exit(self):
        self.exited = True


def test_state_machine_change():
    fsm = StateMachine()
    state1 = MockState()
    state2 = MockState()
    
    fsm.change(state1)
    assert state1.entered
    
    fsm.change(state2)
    assert state1.exited
    assert state2.entered


def test_state_machine_initial_state_is_none():
    fsm = StateMachine()
    assert fsm.state is None