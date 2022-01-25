from typing import Optional

from .events import event_bus

_signal_count = 0  # a simple auto incrementing number for signal id


# noinspection PyPep8Naming
class signal:  # the lowercase is more comfortable in coding (in my feeling).
    """
    code of conduct:
        signal naming convention:
            - use snake case.
            - use passive tense (e.g. 'clicked', 'pressed', 'released', etc.).
    
    warning:
        for the limitation of current design, you must instantiate every signal
        in class's __init__ method.
    
        for example:
            class SomeWidget(Widget):
                
                def __init__(self):
                    self.clicked = signal()
                    
                async def on_clicked(self, event):
                    self.clicked.emit(event)
    
            class AnotherWidget(Widget):
                
                def __init__(self, source_widget):
                    # pass source widget instance as param.
                    source_widget.clicked.connect(self.do_something)
                    
                def do_something(self, event):
                    ...
    """
    _annotations: Optional[tuple]
    _id: int  # FIXME
    
    def __init__(self, *annotations):
        global _signal_count
        _signal_count += 1
        self._annotations = annotations
        self._id = _signal_count
    
    def connect(self, callback):
        event_bus.subscribe(self._id, callback)
    
    def emit(self, *args, **kwargs):
        event_bus.broadcast(self._id, *args, **kwargs)
    
    # async def emit(self, *args, **kwargs):
    #     await event_bus.broadcast(self._id, *args, **kwargs)


# -----------------------------------------------------------------------------
# global signal

def register(name, callback):
    event_bus.subscribe(f'global#{name}', callback)


def emit(name, *args, **kwargs):
    event_bus.broadcast(f'global#{name}', *args, **kwargs)
