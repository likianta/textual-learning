from textual import events
from textual.views import DockView

from ..basic import Button


class Toolbar(DockView):
    
    async def on_mount(self, event: events.Mount) -> None:
        def create_widget():
            btn = Button('XXX')
            return btn
            
        await self.dock(
            create_widget(),
            create_widget(),
            create_widget(),
            edge='left',
            # size=10
        )
