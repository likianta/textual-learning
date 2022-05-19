from rich.console import RenderableType
from rich.text import Text
from textual import events
from textual.widget import Widget

from textual_extensions import signal


class Navigation(Widget):
    """ this is a horizontal scrollable widget.
    
    - use shift + mouse_scroll_up/down to scroll.
    """
    
    def __init__(self, path: str, renderable_size: int):
        super().__init__()
        path = path.strip('/')
        self.on_clicked = signal(int)
        self.on_path_changed = signal(str)
        self._cache = {}  # dict[int mouse_x, int node_index]
        self._highlighted_index = -1
        self._highlighted_node = None
        self._nodes = tuple(map(Node, path.split('/')))
        self._offset = 0
        self._overscroll = len(path) - renderable_size + \
                           (renderable_size // 2)
        self._renderable_size = renderable_size
        
        from textual_extensions import log
        self.on_path_changed.connect(log)
        h = -1
        for i, node in enumerate(self._nodes):
            for j in range(len(node)):
                h += 1
                self._cache[h] = i
    
    def render(self) -> RenderableType:
        start = self._offset
        end = start + self._renderable_size
        # text = Text.assemble(*self._nodes)
        text = Text.assemble(*(
            x.__rich__() for x in self._nodes
        ))
        return text[start:end]
    
    async def on_click(self, event: events.Click) -> None:
        node_index = self._cache[self._offset + event.x]
        if self._highlighted_index == node_index:
            return
        self._highlighted_index = node_index
        
        if self._highlighted_node:
            self._highlighted_node.is_highlighted = False
        new_highlighted_node = self._nodes[node_index]
        new_highlighted_node.is_highlighted = True
        self._highlighted_node = new_highlighted_node
        
        await self.on_clicked.emit(node_index)
        await self.on_path_changed.emit('/' + '/'.join(
            map(str, self._nodes[:node_index + 1])
        ))
        self.refresh()
    
    async def on_mouse_scroll_up(self, event: events.MouseScrollUp):
        if self._offset >= self._overscroll:
            return
        self._offset += event.y
        self.refresh()
    
    async def on_mouse_scroll_down(self, event: events.MouseScrollDown):
        if self._offset <= 0:
            return
        self._offset -= event.y
        self.refresh()


class Node:
    def __init__(self, text: str):
        self.is_highlighted = False
        self._text = text
    
    def __len__(self):
        return len(self._text) + 1  # +1 for the '/'
    
    def __str__(self):
        return self._text
    
    def __rich__(self) -> Text:
        text = Text(self._text, 'red' if self.is_highlighted else 'bright_black')
        text.append('/', 'magenta')
        return text
