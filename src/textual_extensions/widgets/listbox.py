from typing import Optional

from rich.text import Text
from textual.widget import Widget

from .box_layout import VBox
from ..core import signal


class T:
    UID = int
    Item = 'Item'
    Value = str


class ListBox(VBox):
    
    def __init__(self, *names):
        super().__init__()
        
        # chilren holder
        # TODO: use lazy list
        self._uids = []  # list[int uid]. the renderable uids in current scope
        self._all_uids = {}  # dict[int uid, int abs_index]
        self._selected_item = None  # optional[tuple[int uid, item]]
        
        self._id_generator = 0
        self._names = names
        
        self.on_selected = signal(T.UID, T.Value)
    
    async def on_mount(self, event):
        for name in self._names:
            uid = self._gen_uid()
            
            item = Item(uid=uid, text=name, index_ref=self._uids)
            self._uids.append(uid)
            self._all_uids[uid] = item
            
            item.clicked.connect(self._on_item_selected)
            self._widgets.append(item)
        await super().on_mount(event)
        event.prevent_default()
    
    @property
    def selected_item(self) -> Optional['Item']:
        return self._selected_item[1] if self._selected_item else None
    
    def select(self, index: int):
        uid = self._uids[index]
        item = self._all_uids[uid]
        item.select()
    
    def visual_select(self, index: int):
        pass
    
    def _gen_uid(self) -> int:
        self._id_generator += 1
        return self._id_generator
    
    def _on_item_selected(self, uid: int, item: 'Item'):
        if self._selected_item is None:
            self._selected_item = (uid, item)
            self.on_selected.emit(uid, item.text)
            return
        
        last_uid, last_item = self._selected_item
        if last_uid != uid:
            last_item.unselect()
            self._selected_item = (uid, item)
            self.on_selected.emit(uid, item.text)


class Item(Widget):
    
    def __init__(self, uid: int, text: str, index_ref: list):
        super().__init__()
        
        self._text = text
        self._uid = uid
        
        self._selected = False
        self._hovered = False
        # self._focused = Reactive(False)
        # self._hovered = Reactive(False)
        
        self.__index_ref = index_ref  # index reference
        
        self.clicked = signal(int, Item)  # signal[uid]
        # self.hovered = signal(int)  # signal[uid]
    
    def render(self):
        content = Text(overflow="ignore", no_wrap=True)
        index = f'{self._index + 1}. '
        
        if self._selected:
            content.append('> ', 'green bold')
            content.append(index, 'bright_magenta bold')
            if self._hovered:
                content.append(self._text, 'green bold on red')
            else:
                content.append(self._text, 'green bold')
        elif self._hovered:
            content.append('  ')
            content.append(index, 'bright_magenta')
            content.append(self._text, 'default on red')
        else:
            content.append('  ')
            content.append(index, 'bright_magenta')
            content.append(self._text, 'default on default')
        
        content.append("\n")
        return content
    
    @property
    def text(self):
        return self._text
    
    @property
    def _index(self) -> int:
        return self.__index_ref.index(self._uid)
    
    async def on_click(self, event):
        self.select()
        event.prevent_default()
    
    async def on_enter(self):
        self._hovered = True
        self.refresh()
    
    async def on_leave(self):
        self._hovered = False
        self.refresh()
        
    def select(self):
        self._selected = True
        self.refresh()
        self.clicked.emit(self._uid, self)
        
    def unselect(self):
        self._selected = False
        self.refresh()
