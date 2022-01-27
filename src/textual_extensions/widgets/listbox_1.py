"""
inspired by an open source project --
    [kaskade](https://github.com/sauljabin/kaskade):
        kaskade.widgets.topic_list.TopicList
        kaskade.renderable.scrollable_list.ScrollableList
"""
from typing import Generic
from typing import List
from typing import Optional
from typing import TypeVar

from rich.panel import Panel
from rich.text import Text
from textual import events
from textual.keys import Keys
from textual.widget import Widget

from ..core import signal
from ..core import log

T = TypeVar("T")


class ListBox(Widget):
    
    def __init__(
            self,
            *values: str,
            indices: bool = False,
            init_index: int = -1,
            padding: int = 1,
            title: Optional[str] = None,
            **kwargs
    ):
        super().__init__(**kwargs)
        # FIXME: use widget height as default renderable content length
        self._model = Model(list(values), selected=init_index)
        self._options = {
            'indices': indices,
            'padding': padding,
        }
        self._title = title
        
        # signals
        self.added = signal(int, str)
        self.selected = signal(int)
    
    def render(self):
        return Panel(
            self._model,
            padding=(self._options['padding'], 1),
            title=self._title,
            title_align='left',
        )
    
    # -------------------------------------------------------------------------
    
    def add(self, value, index: int = None) -> int:
        if index is None:
            index = len(self._model)
        elif index < 0:  # pick from reverse order.
            index = len(self._model) + index + 1
        self._model.insert(index, value)
        self.added.emit(index, value)
        return index
    
    def select(self, index: int) -> bool:
        # index is absolute.
        is_accepted = self._model.select(index)
        if is_accepted:
            self.refresh()
            self.selected.emit(self._model.selected, self._model.selected_item)
        return is_accepted
    
    # -------------------------------------------------------------------------
    
    async def on_click(self, event):
        pointer = self._get_real_pointer(event)
        log(f'clicking', pointer)
        if pointer is not None and self._model.selected != pointer:
            self._model.selected = pointer
            self.refresh()
            self.selected.emit(self._model.selected, self._model.selected_item)
            return pointer
        return None
    
    async def on_key(self, event: events.Key) -> bool:
        # return (bool):
        #   True if something changed, False otherwise.
        if event.key == Keys.Up:
            if self._model.previous():
                self.refresh()
                self.selected.emit(
                    self._model.selected, self._model.selected_item
                )
                return True
        elif event.key == Keys.Down:
            if self._model.next():
                self.refresh()
                self.selected.emit(
                    self._model.selected, self._model.selected_item
                )
                return True
        return False
    
    # when mouse moves, render the background of hovered item.
    async def on_mouse_move(self, event) -> None:
        pointer = self._get_real_pointer(event)
        if pointer is None:
            pointer = -1
        if self._model.highlighted != pointer:
            self._model.highlighted = pointer
            self.refresh()
    
    def _get_real_pointer(self, event):
        real_pointer = event.y - 1 - self._options['padding']
        if 0 <= real_pointer < self._model.visible_length:
            return real_pointer
        else:
            return None


class Model(Generic[T]):
    # indicators
    _highlighted: int = -1  # relative index
    _selected: int = -1  # relative index
    
    # renderable data
    _values: List[str]
    
    # renderable length
    _start: int = 0
    _count: int = 0
    
    def __init__(
            self,
            values: List[T],
            *,
            count: int = -1,
            selected: int = -1,
    ) -> None:
        self._values = values or []
        
        self._count = count if 0 <= count < len(self._values) \
            else len(self._values)
        self._selected = selected
    
    def __rich__(self) -> Text:
        content = Text(overflow="ignore")
        
        for rel_idx in range(self._count):
            abs_idx = self._start + rel_idx
            
            str_idx = f'{abs_idx + 1}. '
            item = self._values[abs_idx]
            
            if rel_idx == self._selected:
                content.append('> ', 'green bold')
                content.append(str_idx, 'bright_magenta bold')
                if rel_idx == self._highlighted:
                    content.append(item, 'green bold on red')
                else:
                    content.append(item, 'green bold')
            elif rel_idx == self._highlighted:
                content.append('  ')
                content.append(str_idx, 'bright_magenta')
                content.append(item, 'default on red')
            else:
                content.append('  ')
                content.append(str_idx, 'bright_magenta')
                content.append(item, 'default on default')
            content.append("\n")
        
        return content
    
    def __str__(self) -> str:
        return str(self._values[self.start:self.end + 1])
    
    # -------------------------------------------------------------------------
    
    def __len__(self):
        return len(self._values)
    
    def select(self, index: int) -> bool:
        if index >= len(self._values):
            return False
        if self.start <= index <= self.end:
            self._selected = index - self.start
        else:
            self._start = index
            self._selected = 0
        return True
    
    def insert(self, index, value):
        self._values.insert(index, value)
    
    # -------------------------------------------------------------------------
    
    @property
    def start(self):
        return self._start
    
    @property
    def end(self):
        return self._start + self._count - 1
    
    @property
    def visible_length(self):
        return self._count
    
    @property
    def highlighted(self):
        return self._start + self._highlighted
    
    @highlighted.setter
    def highlighted(self, highlighted: int):
        self._highlighted = highlighted
    
    @property
    def selected(self) -> int:
        return self._start + self._selected
    
    @selected.setter
    def selected(self, selected: int):
        self._selected = selected
    
    @property
    def selected_item(self) -> Optional[T]:
        # if self._selected < 0:
        #     return None
        return self._values[self.selected]
    
    def previous(self) -> bool:
        # return:
        #   True: index changed
        #   False: not changed
        log('previous: {} -> {}'.format(self._selected, self._selected - 1))
        if self._selected < 0:
            self._selected = 0
            return True
        elif self._selected > 0:
            self._selected -= 1
            return True
        else:  # self._selected == 0
            if self._start > 0:
                self._start -= 1
                return True
            else:
                return False
    
    def next(self) -> bool:
        log('next: {} -> {}'.format(self._selected, self._selected + 1))
        if self._selected < 0:
            self._selected = 0
            return True
        elif self._selected < self._count - 1:
            self._selected += 1
            return True
        else:  # self._selected == self._count - 1
            if self.end < len(self._values) - 1:
                self._start += 1
                return True
            else:
                return False
    
    def reset(self):
        self._highlighted = -1
        self._selected = -1
        self._start = 0
