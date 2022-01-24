from typing import Optional

from .events import event_bus

_signal_count = 0  # a simple auto incrementing number for signal id


# noinspection PyPep8Naming
class signal:  # the lowercase is more comfortable in coding (in my feeling).
    """
    style guide:
        - use passive voice for signals (e.g. 'clicked', 'changed', ...).
        - define it in the top of class.
    
    examples:
        class SomeWidget(Widget):
            clicked = signal()
            
            async def on_click(self, event):
                self.clicked.emit(event)
        
        class AnotherWidget(Widget):
        
            def __init__(self):
                some_widget = SomeWidget()
                some_widget.clicked.connect(self.do_something)
        
            def do_something(self, *args, **kwargs):
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
