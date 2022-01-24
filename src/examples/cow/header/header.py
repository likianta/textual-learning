from textwrap import dedent
from textwrap import indent

from rich import box
from rich.align import Align
from rich.panel import Panel
from rich.pretty import Pretty
from textual.reactive import Reactive
from textual.widget import Widget


class Header(Widget):
    has_focus = Reactive(False)
    mouse_over = Reactive(False)
    style = Reactive("")
    height = Reactive(None)
    
    def __init__(self, width=80):
        super().__init__(name='Cow Farmland')
        self._header_width = width
    
    def render(self):
        return Panel(
            Align.left(
                # Pretty(
                #     dedent(r'''
                #          \   ^__^
                #           \  (oo)\_______
                #              (__)\       )\/\
                #                  ||----w |
                #                  ||     ||
                #     '''),
                #     # no_wrap=True,
                #     # overflow="ellipsis"
                # ),
                indent(dedent(r'''
                    Welcome to the [bold green]Farmland[/]!
                    
                         \   ^__^
                          \  (oo)\_______
                             (__)\       )\/\
                                 ||----w |
                                 ||     ||
                '''), ' ' * (int(self._header_width / 2) + 7)),
                vertical="middle"
            ),
            title=self.name,
            border_style="green" if self.mouse_over else "blue",
            # border_style='green',
            box=box.ROUNDED,
            style=self.style,
            height=self.height,
        )


r'''
 \   ^__^
  \  (oo)\_______
     (__)\       )\/\
         ||----w |
         ||     ||
'''
