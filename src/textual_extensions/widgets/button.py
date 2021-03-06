from rich.align import Align
from rich.console import RenderableType
from textual.reactive import Reactive

from .widget import Widget
from ..core import signal

__all__ = ['Button']


class Button(Widget):
    hovered = Reactive(False)
    pressed = Reactive(False)
    on_clicked = signal()
    
    def __init__(self, label: str, name: str = None):
        super().__init__(name)
        self.label = label
    
    def __len__(self):
        return len(self.label) + 2
    
    async def on_click(self, event) -> None:
        # await super().on_click(event)
        await self.on_clicked.emit()
    
    async def on_enter(self, _):
        self.hovered = True
    
    async def on_leave(self, _):
        self.hovered = False
    
    async def on_mouse_down(self, _) -> None:
        self.pressed = True
    
    async def on_mouse_up(self, _) -> None:
        self.pressed = False
    
    def render(self) -> RenderableType:
        return Align.center(
            self.label,
            style='white bold on blue3' if self.pressed
            else 'white bold on deep_sky_blue4' if self.hovered
            else 'white on dodger_blue2',
            vertical="middle",
            width=len(self.label) + 2,
            height=1,
        )


class BorderedButton(Button):
    pass  # TODO
