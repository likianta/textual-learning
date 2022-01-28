from rich.console import RenderableType
from textual.widget import Widget


class Button(Widget):
    
    def __init__(self, label: str, padding=1, width=None):
        super().__init__()
        self._enabled = True
        self._label = label
        # self._padding = padding
        self._pressed = False
        self._width = (width or len(label)) + 2 * padding
    
    @property
    def length(self):
        return self._width
    
    def render(self) -> RenderableType:
        label = self._label
        str_spacing = ' ' * ((self._width - len(label)) // 2)
        label = str_spacing + label + str_spacing
        if self._enabled:
            # normal color: light blue on gray
            # pressed color: light blue on dark magenta
            return '[{fg} on {bg}]{label}[/]'.format(
                fg='color(87)',
                bg='#444444' if self._pressed else '#3F298F',
                label=label
            )
        else:
            return '[{fg} on {bg}]{label}[/]'.format(
                fg='color(8)',
                bg='#444444',
                label=label
            )
    
    def set_enabled(self, value: bool):
        if self._enabled != value:
            self._enabled = value
            self.refresh()
    
    async def on_mouse_down(self, event):
        self._pressed = True
        self.refresh()
        event.prevent_default()
    
    async def on_mouse_up(self, event):
        self._pressed = False
        self.refresh()
        event.prevent_default()
