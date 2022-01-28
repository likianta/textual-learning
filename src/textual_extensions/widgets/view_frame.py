"""
inspired by `rich.panel.Panel -> rich.box.ROUNDED`.

usage (1):
    class MyView(DockView):
        async def on_mount(self, event):
            await self.dock(HLine(corner='down'), edge='top', size=1)
            await self.dock(HLine(corner='up'), edge='bottom', size=1)
            await self.dock(VLine(corner=None), edge='right', size=1)
            await self.dock(VLine(corner=None), edge='left', size=1)
            await self.dock(Placeholder(), edge='left')
    # see animated example to understand how it works: TODO
usage (2): we've made a `FrameView` to directly use the frame:
    class MyView(FrameView):
        async def on_mount(self, event):
            await super().on_mount(event)
            await self.dock(Placeholder(), edge='left')

other inspirations (but not used):
    Panel(super().render()):
        https://github.com/Textualize/textual/discussions/79
    rich.style.Style.on(click=...):
        https://github.com/Textualize/textual/discussions/62
"""
from textual.views import DockView
from textual.widget import Widget


class HLine(Widget):
    
    def __init__(self, corner=None):
        # param: corner: optional[literal['up', 'down']]
        super().__init__()
        self._corner = corner
    
    def render(self):
        if self._corner == 'down':
            return '[#444444]╭{}╮[/]'.format('─' * (self._size.width - 2))
        elif self._corner == 'up':
            return '[#444444]╰{}╯[/]'.format('─' * (self._size.width - 2))
        else:
            return '[#444444]{}[/]'.format('─' * self._size.width)


class VLine(Widget):
    
    def __init__(self, corner=None):
        # param: corner: optional[literal['left', 'right']]
        super().__init__()
        self._corner = corner
    
    def render(self):
        if self._corner == 'left':
            return '[#444444]{}[/]'.format('\n'.join((
                '╮', *('│' * (self._size.height - 2)), '╯',
            )))
        elif self._corner == 'right':
            return '[#444444]{}[/]'.format('\n'.join((
                '╭', *('│' * (self._size.height - 2)), '╰',
            )))
        else:
            return '[#444444]{}[/]'.format('\n'.join(
                '│' * self._size.height
            ))


class FrameView(DockView):
    
    async def on_mount(self, event):
        await self.dock(HLine(corner='down'), edge='top', size=1)
        await self.dock(HLine(corner='up'), edge='bottom', size=1)
        await self.dock(VLine(corner=None), edge='right', size=1)
        await self.dock(VLine(corner=None), edge='left', size=1)
