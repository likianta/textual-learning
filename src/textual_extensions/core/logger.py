from inspect import currentframe
from os import getcwd
from os.path import relpath
from typing import Optional

from rich.panel import Panel
from textual.widget import Widget


# TODO: make this widget scrollable
class Logger(Widget):
    _cache: list
    _content_height: int = 2
    # _message: str = ''
    # _source_pos: str = ''
    _working_dir: str = getcwd()
    
    def __init__(self, content_height=1):
        """
        we suggust Logger widget height should be param content_height plus 2
        -- one for upper border line and one for the bottom.
        for example:
            class MyApp(textual.app.App):
                async def on_mount(self):
                    await self.view.dock(
                        Logger(content_height=2),
                        edge='bottom',
                        size=4  # <- content_height + 2
                    )
        """
        super().__init__()
        self._cache = []
        self._content_height = content_height
        global _logger
        _logger = self
    
    def render(self):
        return Panel(
            '\n'.join(self._cache[-self._content_height:]),
            title=f'Logger ({len(self._cache)})', title_align='right'
        )
    
    def log(self, *args, frame=None):
        if not frame:
            frame = currentframe().f_back.f_back
        file_abs = frame.f_globals.get('__file__') or frame.f_code.co_filename
        file_rel = relpath(file_abs, self._working_dir)
        line = frame.f_lineno
        
        source_pos = f'{file_rel}:{line}'
        message = '; '.join(map(str, args)).strip('; ')
        self._cache.append(f'{source_pos} >> {message}')
        self.refresh()
    
    def dump(self, file=''):
        if self._cache:
            from lk_utils import dumps
            from lk_utils.time_utils import timestamp
            dumps('\n'.join(self._cache),
                  file or './log/{}.log'.format(timestamp('ymd-hns')))


_logger = None  # type: Optional[Logger]


def log(*args):
    if _logger is None:
        raise Exception(
            'Logger is not initialized, you should add Logger widget to your '
            'App.on_mount(), and call this function only in the runtime.'
        )
    _logger.log(*args, frame=currentframe().f_back)
