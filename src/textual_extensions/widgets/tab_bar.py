from __future__ import annotations

from rich.align import Align
from rich.console import RenderableType
from textual import events
from textual.reactive import Reactive
from textual.views import DockView
from textual.widgets import Static

from .button import Button
from ..core import signal

__all__ = ['Tabbar']


class TabButton(Button):
    index: int
    checked = Reactive(False)
    on_checked = signal()
    
    def __init__(self, label: str):
        super().__init__(label)
    
    def __len__(self):
        return len(self.label) + 4
    
    async def on_click(self, event: events.Click) -> None:
        # self.checked = True
        self.on_checked.emit(self.index)
    
    def render(self) -> RenderableType:
        # priority: pressed > checked > hovered > default
        if self.pressed:
            label = '[yellow on black]{}[/]'.format(
                '\\[ {} ]'.format(self.label)
            )
        elif self.checked:
            label = '[yellow on bright_black]{}[/]'.format(
                '\\[ {} ]'.format(self.label)
            )
        elif self.hovered:
            label = (
                '[yellow on bright_black]{}[/]'
                '[white on bright_black]{}[/]'
                '[yellow on bright_black]{}[/]'
            ).format(
                '\\[ ', self.label, ' ]'
            )
        else:
            label = '[white on bright_black]  {}  [/]'.format(self.label)
        return Align.center(
            label,
            width=len(self.label) + 4,
            height=1
        )


class Tabbar(DockView):
    # current_index = Reactive(-1)
    
    def __init__(self, *tab_names: str):
        super().__init__()
        self.current_index = -1
        self._tabs = tuple(map(TabButton, tab_names))
    
    def _switch_tab(self, index: int):
        from ..core import log
        log(index)
        last, curr = self.current_index, index
        if last == curr:
            return
        if last == -1:
            self._tabs[curr].checked = True
        else:
            self._tabs[last].checked = False
            self._tabs[curr].checked = True
        self.current_index = curr
    
    async def on_mount(self, event: events.Mount) -> None:
        bar_bg = Static('[default on bright_black]{}[/]'.format(
            ' ' * self.console.size.width
        ))
        
        hbox = DockView()
        for i, t in enumerate(self._tabs):
            t.index = i
            t.on_checked.connect(self._switch_tab)
            await hbox.dock(t, edge='left', size=len(t), z=1)
        
        await self.dock(bar_bg, edge='top', size=1, z=0)
        await self.dock(hbox, edge='top', size=1, z=1)
