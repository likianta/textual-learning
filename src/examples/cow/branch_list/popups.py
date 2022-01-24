from textwrap import dedent

from rich.align import Align
from rich.box import Box
from rich.panel import Panel

from ..basic import Input
from ..core import signal


class NewBranchDialog(Input):
    finished = signal()
    visible: bool
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.visible = False
    
    def render(self):
        out = super().render()
        return Panel(Align.center(out), box=Box(dedent('''\
            │ ││
            │ ││
            ├─┼┤
            │ ││
            ├─┼┤
            ├─┼┤
            │ ││
            ╰─┴╯
        ''')))
    
    async def on_key(self, event):
        await super().on_key(event)
        if event.key == 'enter':
            self.finished.emit(self._typed_chars.text.strip())
            # close self and clear input buffer
            self.visible = False
            self._typed_chars.clear()
        event.prevent_default()
