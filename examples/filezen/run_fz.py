from textual.app import App
from textual.widgets import Placeholder

from textual_extensions import Logger


class MyApp(App):
    
    async def on_mount(self):
        await self.view.dock(Placeholder(), edge='left', size=40)
        await self.view.dock(Logger(), edge='bottom', size=3)
        await self.view.dock(Placeholder(), edge='top')


MyApp.run()
