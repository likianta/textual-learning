from textual.layouts.grid import GridLayout
from textual.layouts.vertical import VerticalLayout
from textual.view import View
from textual.widget import Widget

from .empty_row import EmptyRow


class HBox(View):
    """
    https://github.com/Textualize/textual/blob/main/examples/grid_auto.py
    """
    
    def __init__(self, *widgets: Widget, name=None,
                 gap=None, gutter=None, align=None):
        layout = GridLayout(gap=gap, gutter=gutter, align=align)
        layout.add_column('col', fraction=1, max_size=20)
        layout.add_row('row', fraction=1, max_size=10)
        layout.set_repeat(True, False)
        layout.set_align('stretch', 'start')
        layout.place(*widgets)
        super().__init__(layout=layout, name=name)


class VBox(View):
    
    def __init__(self, *widgets: Widget, name=None,
                 gutter=0):
        layout = VerticalLayout(gutter=gutter)
        #   gutter: union[int, tuple[int, int], tuple[int, int, int, int]]
        #       int: all dimensions.
        #       tuple[int, int]: the first is vertical (top & bottom), the
        #           second is horizontal (left & right).
        #       tuple[int, int, int, int]: top, right, bottom, left.
        
        # the empty row is made for top and bottom "padding".
        layout.add(EmptyRow())
        [layout.add(widget) for widget in widgets]
        layout.add(EmptyRow())
        
        super().__init__(layout=layout, name=name)
