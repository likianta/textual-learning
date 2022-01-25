from textual.views import DockView
from textual.views import GridView
from textual.widget import Widget
from textual.widgets import Placeholder

from ..core import emit
from ..core import log


class Label(Widget):
    def __init__(self, text: str, style=None):
        super().__init__()
        self._style = style or '{}'
        self._text = text
    
    def render(self):
        return self._style.format(self._text)


class _Placeholder1(Placeholder):
    
    async def on_click(self, event):
        log('click on dialog')
        emit('modal')
        # event.prevent_default()


class _Dialog(DockView):
    
    def __init__(self, text='', *, title='', z=1):
        super().__init__()
        self._title = title
        self._text = text
        self._z = z
    
    async def on_mount(self, event):
        # await self.dock(Label(self._title, '[bold]{}[/]'),
        #                 edge='top', size=1, z=self._z)
        # await self.dock(Placeholder(),
        #                 edge='bottom', size=3, z=self._z)  # buttons
        # await self.dock(Label(self._text),
        #                 edge='top', z=self._z)
        await self.dock(_Placeholder1(), z=self._z)


class Dialog(GridView):
    """
    references:
        grid layout example:
            pass
        auto grid layout example:
            https://github.com/Textualize/textual/blob/4d94df81e44b27fff52f0e38f
            4f109212e9e8c8a/examples/grid_auto.py
    """
    
    def __init__(self, text: str, title='', z=1):
        super().__init__()
        self._text = text
        self._title = title
        self._z = z
    
    async def on_mount(self, event):
        self.grid.add_column('col', fraction=1, max_size=20)
        self.grid.add_row('row', fraction=1, max_size=10)
        self.grid.set_repeat(True, True)
        self.grid.add_areas(center='col-2-start|col-4-end,row-2-start|row-3-end')
        self.grid.set_align('stretch', 'center')
        self.grid.place(center=_Dialog(self._text, title=self._title, z=self._z))
