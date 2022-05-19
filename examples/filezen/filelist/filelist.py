import os

from textual import events
from textual.keys import Keys

from textual_extensions import FrameView
from textual_extensions import ListBox
from textual_extensions import log
from textual_extensions import signal
from .navigation import Navigation


class FileListView(FrameView):
    
    def __init__(self, path: str, renderable_size: int):
        super().__init__()
        self._path = path
        self._renderable_size = renderable_size
        
        self._navi = None
        self._filelist = None
        
        self.on_list_duplicated = signal()
    
    async def on_mount(self, event: events.Mount) -> None:
        self._navi = Navigation(self._path, self._renderable_size)
        self._filelist = FileList(self._path)
        self._navi.on_clicked.connect(lambda *_: self._filelist.focus(), True)
        self._navi.on_path_changed.connect(self._filelist.change_directory)
        self._filelist.on_list_duplicated.connect(self.on_list_duplicated)
        await super().on_mount(event)
        await self.dock(self._navi, edge='top', size=1)
        await self.dock(self._filelist, edge='top')


class FileList(ListBox):
    def __init__(self, directory: str):
        super().__init__(*os.listdir(directory))
        self._dir = directory
        self.on_list_duplicated = signal(str)
        
    def change_directory(self, directory: str):
        log(directory)
        self._dir = directory
        self.items = os.listdir(self._dir)
        self.refresh()
    
    async def on_key(self, event):
        if event.key == Keys.ControlP:
            self._copy_to_clipboard(self.selected_path)
            log('path copied', self.selected_path)
        elif event.key == Keys.ControlD:
            # await self.app.add_filelist_2(self.selected_path)
            await self.on_list_duplicated.emit(self.selected_path)
            log('you preesed ctrl+d', self.selected_path)
    
    @property
    def selected_path(self):
        return self._dir + '/' + self.selected_item

    @staticmethod
    def _copy_to_clipboard(s: str):
        """
        https://blog.csdn.net/My_CSDN_IT/article/details/114122199
        """
        from tkinter import Tk
        r = Tk()
        r.withdraw()
        r.clipboard_clear()
        r.clipboard_append(s)
        r.update()
        r.destroy()
