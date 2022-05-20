from textual.keys import Keys

from ..core import signal

__all__ = ['FocusScope', 'Focusable', 'global_focus_scope']


class IdGenerator:
    def __init__(self):
        self._cnt = 0
    
    def gen_id(self):
        self._cnt += 1
        return self._cnt


class FocusScope:
    
    def __init__(self):
        self.on_focus_changed = signal()
        self._id_gen = IdGenerator()
        self.__items_list = []  # list[int uid]
        self.__items_dict = {}  # dict[int uid, Focusable]
        self.__last_focused = None  # optional[tuple[int uid, Focusable]]
    
    def add(self, uid, item):
        self.__items_list.append(uid)
        self.__items_dict[uid] = item
    
    async def change_focus(self, uid, item):
        if self.__last_focused is not None:
            last_uid, last_item = self.__last_focused
            if last_uid != uid:
                last_item.lose_focus(_notify=False)
                self.__last_focused = (uid, item)
                await self.on_focus_changed.emit(uid, item)
        else:
            self.__last_focused = (uid, item)
            await self.on_focus_changed.emit(uid, item)
    
    def gen_id(self):
        return self._id_gen.gen_id()
    
    def focus_prev(self):
        current_index = self.__items_list.index(self.__last_focused[0])
        if current_index > 0:
            last_index = current_index - 1
            last_uid = self.__items_list[last_index]
            last_item = self.__items_dict[last_uid]
        else:
            last_index = len(self.__items_list) - 1
            last_uid = self.__items_list[last_index]
            last_item = self.__items_dict[last_uid]
        last_item.gain_focus()
        # self.change_focus(last_uid, last_item)
    
    def focus_next(self):
        current_index = self.__items_list.index(self.__last_focused[0])
        if current_index < len(self.__items_list) - 1:
            next_index = current_index + 1
            next_uid = self.__items_list[next_index]
            next_item = self.__items_dict[next_uid]
        else:
            next_index = 0
            next_uid = self.__items_list[next_index]
            next_item = self.__items_dict[next_uid]
        next_item.gain_focus()
        # self.change_focus(next_uid, next_item)


global_focus_scope = FocusScope()


class Focusable:
    
    def __init__(self, scope: FocusScope = None):
        self._focused = False
        self._scope = scope or global_focus_scope
        self._uid = self._scope.gen_id()
        self.on_focused = signal(int, Focusable)
        # self.on_focus_changed = signal(int, bool)
        #   param#2: bool: True if goes to next, False goes to previous.
        
        self.on_focused.connect(self._scope.change_focus, is_async=True)
        self._scope.add(self._uid, self)
    
    async def gain_focus(self, _notify=True):
        self._focused = True
        if _notify:
            await self.on_focused.emit(self._uid, self)
    
    def lose_focus(self, _notify=True):  # DELETE: param not used
        self._focused = False
        # if _notify:
        #     self.on_focused.emit(self._uid, self)
    
    async def on_key(self, event):
        if event.key == Keys.Tab:
            self._scope.focus_next()
        elif event.key == 'shift+tab':  # fix: textual doesn't have Keys.ShiftTab
            self._scope.focus_prev()
