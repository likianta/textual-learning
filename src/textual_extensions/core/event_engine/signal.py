from .events import event_bus

_signal_count = 0  # a simple auto increment counter for generating signal ids.


# noinspection PyPep8Naming
class signal:
    """
    (i'm using lowercase for class name, the lowercase feels more comfortable
     in my opinion.)
    
    code of conduct:
        signal naming convention:
            - use snake case.
            - use passive tense (e.g. 'clicked', 'pressed', 'released', etc.).
    
    warning:
        for the limitation of current design, you must instantiate every signal
        in class's __init__ method.
    
        for example:
            class SomeWidget(Widget):
                # wrong
                pressed = signal()
                
                def __init__(self):
                    # right
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
    _annotations: tuple
    _id: int  # FIXME
    
    def __init__(self, *annotations):
        global _signal_count
        _signal_count += 1
        self._annotations = annotations
        self._id = _signal_count
    
    def connect(self, callback, is_async=False):
        # FIXME: asyncio.coroutine.iscoroutine function is not available to
        #   check if the callback is a coroutine. (i don't know why)
        #   so if you are passing an async callback, you must set
        #   `is_async=True` explicitly.
        if isinstance(callback, signal):
            event_bus.subscribe(self._id, callback.emit, True)
        else:
            event_bus.subscribe(self._id, callback, is_async)
    
    async def emit(self, *args, **kwargs):
        await event_bus.broadcast(self._id, *args, **kwargs)


# -----------------------------------------------------------------------------
# global signal
# this would be friendly to simple use cases.

def listen(name, callback):
    event_bus.subscribe(f'global#{name}', callback)


def emit(name, *args, **kwargs):
    event_bus.broadcast(f'global#{name}', *args, **kwargs)
