# noinspection PyPep8Naming
class signal:
    
    def __init__(self):
        self._slots = {}
    
    def connect(self, slot):
        self._slots[id(slot)] = slot
    
    def disconnect(self, slot):
        del self._slots[id(slot)]
    
    def emit(self, *args, **kwargs):
        for slot in self._slots.values():
            slot(*args, **kwargs)


# TODO: below is not considered to be formal released yet.
# noinspection PyPep8Naming
class slot:
    
    def __init__(self, callback):
        self.callback = callback
    
    def __call__(self, *args, **kwargs):
        self.callback(*args, **kwargs)
