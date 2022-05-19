from textual.widget import Widget


class Spacer(Widget):
    def __init__(self, pattern=' '):
        super().__init__()
        self._pattern = pattern
        
    def render(self):
        return self._pattern


class HSpacer(Widget):
    """ horizontal spacer. """
    
    def __init__(self, placeholder=' '):
        super().__init__()
        self._placeholder = placeholder
    
    def render(self):
        return self._placeholder * self._size.width


class VSpacer(Widget):
    """ vertical spacer. """
    
    def __init__(self, placeholder=' '):
        super().__init__()
        self._placeholder = placeholder
    
    def render(self):
        return '\n'.join(self._placeholder * self._size.height)
