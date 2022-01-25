from textual import events
from textual.app import App
from textual.views import GridView
from textual.widgets import Placeholder


class MyView(GridView):
    """
    we use GridView to layout buttons in a row.
    """
    
    async def on_mount(self, event: events.Mount) -> None:
        self.grid.add_column('col', fraction=1, repeat=3)
        self.grid.add_row('row', fraction=1)
        self.grid.set_gap(1, 0)
        self.grid.place(
            Placeholder(name='button1'),
            Placeholder(name='button2'),
            Placeholder(name='button3'),
        )


class MyApp(App):
    async def on_mount(self):
        await self.view.dock(MyView(), edge='top', size=3)


MyApp.run()
