from textual.widget import Widget


class HSpacing(Widget):
    
    def __init__(self, height: int = 1):
        super().__init__()
        self._height = height
    
    def render(self):
        return '\n'.join((' ' * self._size.width,) * self._height)


class VSpacing(Widget):
    
    def __init__(self, width=1):
        super().__init__()
        self._width = width
    
    def render(self):
        return ' ' * self._width


# Spacing = VSpacing
# EmptyRow = HSpacing
