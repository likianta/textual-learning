from textual import events
from textual.views import DockView

from .details import BranchDetails as _Details
from .toolbar import Toolbar


class BranchDetails(DockView):
    async def on_mount(self, event: events.Mount) -> None:
        await self.dock(Toolbar(), edge='bottom', size=3)
        await self.dock(_Details(), edge='top')
