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
        self._last_selected = None  # optional[tuple[int uid, Focusable]]
    
    def change_focus(self, uid, item):
        if self._last_selected is not None:
            last_uid, last_item = self._last_selected
            if last_uid != uid:
                last_item.lose_focus(_notify=False)
                self._last_selected = (uid, item)
                self.on_focus_changed.emit(uid, item)
        else:
            self._last_selected = (uid, item)
            self.on_focus_changed.emit(uid, item)
    
    def gen_id(self):
        return self._id_gen.gen_id()


global_focus_scope = FocusScope()


class Focusable:
    
    def __init__(self, scope: FocusScope = None):
        self.__scope = scope or global_focus_scope
        self._uid = self.__scope.gen_id()
        self._focused = False
        self.on_focused = signal(int, Focusable)
        self.on_focused.connect(self.__scope.change_focus)
    
    def gain_focus(self, _notify=True):
        self._focused = True
        if _notify:
            self.on_focused.emit(self._uid, self)
    
    def lose_focus(self, _notify=True):  # DELETE: param not used
        self._focused = False
        # if _notify:
        #     self.on_focused.emit(self._uid, self)
