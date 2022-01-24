from rich.align import Align
from rich.console import RenderableType
from textual.reactive import Reactive
from textual.widget import Widget


class Button(Widget):
    pressed = Reactive(False)
    
    def __init__(self, label: str, padding=1):
        super().__init__()
        self._label = label
        self._padding = padding
    
    def render(self) -> RenderableType:
        # normal color: light blue on gray
        # pressed color: light blue on dark magenta
        
        label = '{0}{1}{0}'.format(
            ' ' * self._padding,
            self._label
        )
        
        return Align.center('[{fg} on {bg}]{label}[/]'.format(
            fg='color(87)',
            bg='#444444' if self.pressed else '#3F298F',
            label=label
        ))
