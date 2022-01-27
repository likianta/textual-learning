from textual.app import App
from textual.widgets import Placeholder

from textual_extensions import event_bus


class MyApp(App):
    
    async def on_mount(self):
        await self.view.dock(Placeholder(), edge='left', size=40)
        await self.view.dock(Placeholder(), edge='bottom', size=3)
        await self.view.dock(Placeholder(), edge='top')


MyApp.run()
event_bus.close()
