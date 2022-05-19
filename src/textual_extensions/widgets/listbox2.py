"""
widget based listbox.
"""
from rich.text import Text
from textual.widget import Widget


class ListBox(Widget):
    
    def __init__(self, *items,
                 renderable_size=None, 
                 step_size=3, 
                 overscroll_size='half',
                 _home_key_behaviors=('most_start', 'most_start'),
                 _end_key_behaviors=('page_end', 'most_end')):
        """
        args:
            items: iter[str]
            renderable_size: optional[int]
                None: render all items
                int: render at most this many items, it is allowed to use a
                    value bigger than len(items).
            step_size: int
            overscroll_size: literal['none', 'half', 'full'].
                when scroll to the end, how much empty space to render in the
                bottom:
                    'none': do not render.
                    'half': render half page (renderable_size // 2).
                    'full': leave one item in the top, render the rest zone.
            _home_key_behaviors: tuple[literal, lieteral]
                literal#1: how to handle the key 'home'.
                    type: literal[
                        'none', 'page_start', 'most_start', 'page_most_start'
                    ]
                    default: 'most_start'
                    description:
                        none: do nothing.
                        page_start: move to the start of the page.
                        most_start: move to the most start of the full list.
                        page_most_start: if current selected index is not in 
                            the start of the page, move to the page-start; 
                            otherwise move to the most-start.
                literal#2: how to handle the key 'ctrl + home'.
                    type: literal['none', 'most_start']
                    default: 'most_start'
            _end_key_behaviors: tuple[literal, lieteral]
                literal#1: how to handle the key 'end'.
                    type: literal[
                        'none', 'page_end', 'most_end', 'page_most_end'
                    ]
                    default: 'page_end'.
                literal#2: how to handle the key 'ctrl + end'.
                    type: literal['none', 'most_end']
                    default: 'most_end'
        """
        super().__init__()
        self.items = items
        
        # relative index
        #   start from 0, but -1 for non-focused index.
        self._selected_index = -1
        self._highlighted_index = -1
        
        self._renderable_size = renderable_size or len(items)
        self._start = 0
        self._step_size = step_size
        self._overscroll_size = overscroll_size
        
        self._home_key_behaviors = _home_key_behaviors
        self._end_key_behaviors = _end_key_behaviors

        # ---------------------------------------------------------------------
        
        self._is_scrollable = len(self.items) > self._renderable_size
    
    @property
    def selected_item(self):
        if self._selected_index >= 0:
            return self.items[self._start + self._selected_index]
    
    @property
    def _end(self) -> int:
        # rule of scope: start <= <current_index> < end
        return min((self._start + self._renderable_size, len(self.items)))
    
    @property
    def _most_end(self) -> int:
        if self._overscroll_size == 'none':
            return len(self.items)
        elif self._overscroll_size == 'half':
            return len(self.items) + self._renderable_size // 2
        elif self._overscroll_size == 'full':
            return len(self.items) + self._renderable_size - 1
            #   -1 for the last item.

    # -------------------------------------------------------------------------
    
    def render(self):
        text = Text()
        
        for rel_idx in range(self._renderable_size):
            abs_idx = self._start + rel_idx
            if abs_idx >= len(self.items):
                break
            str_idx = f'{abs_idx + 1}. '
            item = self.items[abs_idx]
            
            if rel_idx == self._selected_index:
                text.append(f'> ', 'green bold')
                text.append(str_idx, 'magenta bold')
            else:
                text.append(f'  ')
                text.append(str_idx, 'magenta')
            
            if rel_idx == self._highlighted_index:
                if rel_idx == self._selected_index:
                    text.append(item, 'green bold on red')
                else:
                    text.append(item, 'default on red')
                if (rest_space := (
                        self._size.width - 2 - len(str_idx) - len(item)
                )) > 0:
                    text.append(' ' * rest_space, 'on red')
            elif rel_idx == self._selected_index:
                text.append(item, 'green bold')
            else:
                text.append(item)
                
            text.append('\n')
        
        return text
    
    # -------------------------------------------------------------------------
    
    async def on_click(self, event):
        self._selected_index = event.y
        self.refresh()
    
    async def on_key(self, event):
        # TODO: pageup, pagedown, ctrl + home, ctrl + end.
        if event.key == 'up':
            self._to_prev_item()
        elif event.key == 'down':
            self._to_next_item()
        elif event.key == 'home':
            behavior = self._home_key_behaviors[0]
            if behavior == 'none':
                return
            elif behavior == 'page_start':
                self._to_page_start()
            elif behavior == 'most_start':
                self._to_most_start()
        elif event.key == 'end':
            behavior = self._end_key_behaviors[0]
            if behavior == 'none':
                return
            elif behavior == 'page_end':
                self._to_page_end()
            elif behavior == 'most_end':
                self._to_most_end()
    
    async def on_mouse_move(self, event):
        self._highlighted_index = event.y
        self.refresh()
    
    async def on_mouse_scroll_up(self, _):
        # note: in textual, (look through left side of your mouse), the
        #   close-wise is mouse scroll up. (it is different with windows.)
        if self._is_scrollable:
            end = self._start + self._renderable_size
            if end < self._most_end:
                self._start += self._step_size
                self._selected_index -= self._step_size
                self.refresh()
    
    async def on_mouse_scroll_down(self, _):
        if self._is_scrollable:
            if self._start > 0:
                self._start -= self._step_size
                self._selected_index += self._step_size
                self.refresh()
    
    # -------------------------------------------------------------------------
    
    def _to_prev_item(self):
        if self._selected_index == -1:
            self._selected_index = 0
        elif self._selected_index > 0:
            self._selected_index -= 1
        else:
            return
        self.refresh()
    
    def _to_next_item(self):
        if self._selected_index == -1:
            self._selected_index = 0
        elif self._selected_index < self._renderable_size - 1:
            self._selected_index += 1
        else:  # we are at the end of current page.
            if self._start + self._selected_index < len(self.items) - 1:
                self._start += 1
            else:
                return
        self.refresh()
    
    def _to_prev_page(self):
        if self._start > 0:
            old, new = self._start, max(
                (self._start - self._renderable_size, 0)
            )
            self._start = new
            self._selected_index += abs(new - old)
            # self._selected_index = min(
            #     (self._selected_index + abs(new - old), self._page_end)
            # )
            self.refresh()
    
    def _to_next_page(self):
        new_start = self._start + self._renderable_size
        new_end = new_start + self._renderable_size
        if new_end < self._most_end:
            old, new = self._start, new_start
            self._start = new
            self._selected_index -= abs(new - old)
            self.refresh()

    def _to_page_start(self):
        if self._selected_index != 0:
            self._selected_index = 0
            self.refresh()
    
    def _to_page_end(self):
        end = self._start + self._renderable_size
        if end <= len(self.items):
            self._selected_index = self._renderable_size - 1
        else:
            self._selected_index = self._renderable_size - \
                                   (end - len(self.items)) - 1
        self.refresh()
    
    def _to_most_start(self):
        if self._selected_index == 0 and self._start == 0:
            return
        self._selected_index = 0
        self._start = 0
        self.refresh()
    
    def _to_most_end(self):
        self._selected_index = min(
            (self._renderable_size - 1, len(self.items) - 1)
        )
        self._start = max(
            (len(self.items) - self._renderable_size, 0)
        )
        self.refresh()

    to_prev = _to_prev_item
    to_next = _to_next_item
    to_home = _to_most_start
    to_end = _to_most_end
