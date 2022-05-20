from .events import event_bus

_signal_count = 0  # a simple auto increment counter for generating signal ids.


class SignalSupport:
    def __init__(self):
        for k, v in self.__class__.__dict__.items():
            if k.endswith('ed'):
                if isinstance(v, signal):
                    self.__dict__[k] = signal()


# noinspection PyPep8Naming
class signal:
    """
    (i'm using lowercase for class name, the lowercase feels more comfortable
     in my opinion.)
    
    code of conduct:
        signal naming convention:
            -   use snake case.
            -   use passive tense. (i.e. the name ends with 'ed', for example
                'clicked', 'pressed', 'released', etc.)
                notice:
                    this is a MANDATORY format. for names which is not
                    'ed'-ended, it won't be detected, then it may lead to
                    unexpected behaviors.
                    this is because we have implemented a magic method to
                    accept only 'ed'-ended names. see also `../../widgets/
                    widget.py : class Widget` for more information.
            -   suggest using 'on_' as common prefix. for example 'on_clicked',
                'on_pressed', 'on_released', etc.
                
    experimental:
        currently (0.1.0) we support declaring signals in class-level. the
        following code is allowed:
            from textual_extensions import Widget
            class SomeWidget(Widget):
                on_pressed = signal()
                ...
        the only thing keeps in mind is that using `from textual_extensions
        import Widget`, instead of `from textual.widget import Widget`.
        you can check its source code to find how is it implemented.
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
