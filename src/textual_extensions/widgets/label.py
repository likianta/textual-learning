from rich.text import Text
from textual.widget import Widget


class Label(Widget):
    
    def __init__(self, text: str, align='default'):
        # align: literal['default', 'left', 'center', 'right']
        super().__init__(name=text)
        self._align = align
    
    @property
    def length(self):
        return len(self.name)
    
    def render(self):
        return Text(self.name, justify=self._align)  # type: ignore
