from textual.widget import Widget as BaseWidget

from ..core.event_engine import SignalSupport

__all__ = ['Widget']


class Widget(BaseWidget, SignalSupport):
    def __init__(self, name=None):
        BaseWidget.__init__(self, name)
        SignalSupport.__init__(self)
