from typing import Optional

from rich.align import Align
from rich.panel import Panel
from textual import events
from textual.app import App
from textual.geometry import Size
from textual.views import DockView
from textual.widget import Widget
from textual.widgets import Placeholder

from ..basic import Button
from ..core import emit
from ..core import log
from ..registered_events import BRANCH_TOOLBAR_CLICKED


class AddButton(Button):
    
    def __init__(self):
        super().__init__('Add')
    
    async def on_click(self, event):
        emit('switch_new_branch_dialog')
        event.prevent_default()


# TODO: more custom buttons


class Toolbar(Widget):
    _button_map: dict = None
    _button_names: list
    _buttons: list
    _padding: int = 1
    _spacing: int = 1
    
    def __init__(self, padding=1, spacing=1):
        super().__init__()
        self._button_names = ['Add', 'Remove', 'Rename']  # DELETE
        self._buttons = [AddButton()] + \
                        [Button(x) for x in self._button_names[1:]]  # noqa
        self._padding = padding
        self._spacing = spacing
    
    def render(self):
        return Panel((' ' * self._spacing).join(
            x.render() for x in self._buttons
        ), padding=(0, self._padding))
        #   [param#2] padding: tuple[int vertical, int horizontal]
    
    async def on_click(self, event: events.Click):
        btn_idx = self._which_button_am_i_clicking(event.x)
        if btn_idx is not None:
            label = self._button_names[btn_idx]
            log('button clicked: {}'.format(label))
            emit(BRANCH_TOOLBAR_CLICKED, label)
            await self._buttons[btn_idx].on_click(event)
        else:
            log('no button clicked')
        event.prevent_default()
    
    async def on_mouse_down(self, event: events.MouseDown):
        btn_idx = self._which_button_am_i_clicking(event.x)
        if btn_idx is None:
            return
        self._buttons[btn_idx].pressed = True
        self.refresh()
        event.prevent_default()
    
    async def on_mouse_up(self, event: events.MouseUp):
        btn_idx = self._which_button_am_i_clicking(event.x)
        if btn_idx is None:
            return
        self._buttons[btn_idx].pressed = False
        self.refresh()
        event.prevent_default()
    
    def _which_button_am_i_clicking(self, x: int) -> Optional[int]:
        """ detect button index by x-coordinate. """
        if self._button_map is not None:
            return self._button_map.get(x)
        
        mapping = {}  # dict[int x_pos, int button_index]
        abs_idx = self._padding  # absolute index. 1 for left padding.
        #   this index is pointed to the position of char.
        #   illustration:
        #       bla|bla...      <- the cursor `|` is not our index, `^` is.
        #           ^
        for btn_idx, btn_name in enumerate(self._button_names):
            for _ in range(len(btn_name) + 2):
                abs_idx += 1
                mapping[abs_idx] = btn_idx
            abs_idx += self._spacing  # jump spacing
        
        self._button_map = mapping
        return self._button_map.get(x)


class NewBranchDialog(DockView):
    
    async def on_mount(self, event):
        await self.dock(Placeholder(), edge='top', size=10, z=1)
        await self.dock(Close(), edge='top', size=3, z=1)


class Close(Widget):
    
    def render(self):
        return Panel(Align.center('Close', vertical='middle'))
    
    async def on_click(self, event):
        await pop_view(self.app)
        event.prevent_default()


async def center_align_view(app: App, view: DockView, width: int, height: int):
    from ..basic import EmptyRow
    screen_size = app.console.size  # namedtuple[int width, int height]
    view_size = Size(width, height)  # the same type as screen_size
    
    x = (screen_size.width - view_size.width) // 2
    y = (screen_size.height - view_size.height) // 2
    await app.view.dock(EmptyRow(), edge='left', size=x, z=1)
    await app.view.dock(EmptyRow(), edge='top', size=y, z=1)
    await app.view.dock(EmptyRow(), edge='right', size=x, z=1)
    await app.view.dock(view, edge='top', size=height, z=1)

    app.refresh(True, True)


# noinspection PyProtectedMember
async def pop_view(app):
    if len(app._view_stack) > 1:
        view = app._view_stack.pop()
        await app.remove(view)
        app.refresh()
