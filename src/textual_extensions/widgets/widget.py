from textual.widget import Widget as BaseWidget

from ..core import signal

__all__ = ['Widget']


class Widget(BaseWidget):
    
    def __init__(self, name=None):
        super().__init__(name)
        for k, v in self.__class__.__dict__.items():
            if k.endswith('ed'):
                if isinstance(v, signal):
                    self.__dict__[k] = signal()
