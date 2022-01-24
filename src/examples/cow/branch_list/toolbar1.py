from rich.console import RenderableType
from rich.panel import Panel
from textual import events
from textual.views import DockView
from textual.widget import Widget

from ..basic import Button


class Background(Widget):
    def render(self) -> RenderableType:
        return Panel('')


class Toolbar(DockView):
    async def on_mount(self, event: events.Mount) -> None:
        await self.dock(Background())
        await self.dock(
            Button('Add'),
            Button('Remove'),
            Button('Rename'),
            edge='left',
        )
