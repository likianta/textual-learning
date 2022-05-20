from string import printable

from textual import events
from textual.keys import Keys
from textual.reactive import Reactive
from textual.widget import Widget

from .focus_scope import Focusable


class Input(Widget, Focusable):
    # TODO: features in progress:
    #   - copy, clip and paste
    #   - selection (mouse selection and keyboard selection)
    #   - jump by word (ctrl + left, ctrl + right)
    #   - auto complete (popup or inline prompt text)
    # FIXME:
    #   - when text is too long to show, the cursor will be out of the visible
    #     zone.
    submit_data = Reactive(None)
    _focused = Reactive(False)
    _padding: int
    _placeholder = ''
    _typed_chars: 'TypedChars'
    
    def __init__(
            self, text='', placeholder='', *,
            cursor_blink=True, cursor_bold=False, cursor_shape='_',
            focus_scope=None, padding=1,
    ):
        """
        args:
            text: str
            placeholder: str
            cursor_bold: bool
            cursor_shape: literal['_', '|', '▉']
            padding: int
        """
        Widget.__init__(self)
        Focusable.__init__(self, focus_scope)
        #   Focusable provides:
        #       self._focused: bool
        #       self.gain_focus()
        #       self.lose_focus()
        #       self.on_focused: signal
        self._padding = padding
        self._placeholder = placeholder
        self._typed_chars = TypedChars(
            text,
            blink=cursor_blink,
            bold=cursor_bold,
            shape=cursor_shape
        )
    
    def render(self):
        if self._focused:
            # notice:
            #   there is a point that, if cursor shape is '_' or '▉', and the
            #   cursor is at the end, `self._typed_chars` has to add an
            #   additional whitespace to make sure tailed cursor can be
            #   rendered. but we need to strip this whitespace otherwise it
            #   causes `self._fill_bg` incorrect its background width.
            # noinspection PyProtectedMember
            if self._typed_chars._cursor.shape != '|' and \
                    self._typed_chars and \
                    self._typed_chars._is_end:
                rich_text = self._fill_bg(
                    self._typed_chars.rich_text_with_cursor,
                    len(self._typed_chars.text_with_cursor) + 1  # <- +1
                )
            else:
                rich_text = self._fill_bg(
                    self._typed_chars.rich_text_with_cursor,
                    len(self._typed_chars.text_with_cursor)
                )
        else:
            if self._typed_chars:
                rich_text = self._fill_bg(
                    self._typed_chars.rich_text,
                    len(self._typed_chars.text)
                )
            else:  # show placeholder.
                rich_text = self._fill_bg(
                    # a little darker on grey background.
                    '[#ABA7B9 on #444444]{}[/]'.format(self._placeholder),
                    len(self._placeholder)
                )
        
        return '[default on #444444]{0}{1}{0}[/]'.format(
            ' ' * self._padding, rich_text
        )
    
    # -------------------------------------------------------------------------
    
    # == events ==
    
    async def on_click(self, event: events.Click):
        # await self.gain_focus()
        await self.gain_focus()
        self._typed_chars.activate(event.x - self._padding)
        self.refresh()
        event.prevent_default()
    
    async def on_key(self, event: events.Key):
        event.prevent_default()
        
        # normal inputs
        is_changed = None
        if event.key in printable:
            is_changed = self._typed_chars.add(event.key)
        
        # manipulate existed chars and move cursor
        
        elif event.key in (Keys.Backspace, Keys.ControlH):
            # backspace is recognized as `control + h` in unix system.
            is_changed = self._typed_chars.del_left()
        
        elif event.key == Keys.Delete:
            is_changed = self._typed_chars.del_right()
        
        # focus changed
        
        elif event.key == Keys.Enter:
            self.submit_data = self._typed_chars.text
            self._focused = False
            is_changed = True
        
        elif event.key == Keys.Escape:
            self._focused = False
            is_changed = True
        
        elif event.key in (Keys.Tab, Keys.ControlI):
            self._scope.focus_next()
        
        elif event.key == 'shift+tab':
            self._scope.focus_prev()
        
        # navigation
        
        elif event.key == Keys.End:
            is_changed = self._typed_chars.move('end')
        elif event.key == Keys.Home:
            is_changed = self._typed_chars.move('start')
        elif event.key == Keys.Left:
            is_changed = self._typed_chars.move('left')
        elif event.key == Keys.Right:
            is_changed = self._typed_chars.move('right')
        
        if is_changed is True:
            self.refresh()
    
    async def watch__focused(self, focus: bool):
        if focus:
            await self.focus()
        self.refresh()  # inherit from `Widget`
    
    # == properties ==
    
    @property
    def length(self):
        return len(self._typed_chars)
    
    @property
    def text(self):
        return self._typed_chars.text
    
    # == other ==
    
    @property
    def _content_width(self):
        return self._size.width - self._padding * 2
    
    def _fill_bg(self, text: str, length=None):
        if length is None:
            length = len(text)
        if length < self._content_width:
            text += ' ' * (self._content_width - length)
        return text
    
    # def lose_focus(self, _notify=True):
    #     super().lose_focus(_notify)
    #     self.refresh()
    
    def set_text(self, text: str):
        if self._typed_chars.text != text:
            self._typed_chars = TypedChars(
                # FIXME: use TypedCharsFactory to re-create TypedChars instance.
                text, cursor_bold=True, cursor_shape='_'
            )
            self.refresh()


class TypedChars:
    _cursor: 'Cursor'
    _typed_chars: list
    
    def __init__(self, text: str = '', **cursor_kwargs):
        self._cursor = Cursor(**cursor_kwargs)
        self._typed_chars = [x for x in text]
    
    def __bool__(self):
        return bool(self._typed_chars)
    
    def __len__(self):
        return len(self._typed_chars)
    
    # @property
    # def length(self):
    #     return len(self._typed_chars)
    
    # @property
    # def index(self):
    #     return self._cursor.index
    
    @property
    def _is_start(self):
        return self._cursor.index <= 0
    
    @property
    def _is_end(self):
        return self._cursor.index == len(self._typed_chars)
    
    # -------------------------------------------------------------------------
    # manipulate existed chars and/or move cursor.
    # return: bool
    #   True: typed chars and/or cursor index changed.
    #   False: nothing changed.
    
    def add(self, char: str) -> bool:
        if self._is_end:
            self._typed_chars.append(char)
            self._cursor.to_right()
            return True
        else:
            self._typed_chars.insert(self._cursor.index, char)
            self._cursor.to_right()
            return True
    
    def del_left(self):
        if not self._typed_chars:
            return False
        if self._is_end:
            self._typed_chars.pop()
            self._cursor.to_left()
            return True
        else:
            self._typed_chars.pop(self._cursor.index - 1)
            self._cursor.to_left()
            return True
    
    def del_right(self) -> bool:
        if not self._typed_chars or self._is_end:
            return False
        else:
            self._typed_chars.pop(self._cursor.index)
            return True
    
    # alias
    ldel = del_left
    rdel = del_right
    
    def clear(self) -> bool:
        if not self._typed_chars:
            return False
        self._typed_chars.clear()
        self._cursor.to_start()
        return True
    
    def move(self, to: str) -> bool:
        """
        args:
            to: literal['start', 'left', 'right', 'end']
        """
        if to == 'start' or to == 'home':
            return self._cursor.to_start()
        elif to == 'left':
            return self._cursor.to_left()
        elif to == 'right':
            return self._cursor.to_right(len(self._typed_chars))
        elif to == 'end':
            return self._cursor.to_end(len(self._typed_chars))
        else:
            raise ValueError('invalid move direction: {}'.format(to))
    
    def activate(self, x: int) -> bool:
        self._cursor.activate(x, len(self._typed_chars))
        return True
    
    # -------------------------------------------------------------------------
    
    @property
    def rich_text(self):
        return '[default]{}[/]'.format(''.join(self._typed_chars))
    
    @property
    def rich_text_with_cursor(self):
        if not self._typed_chars:
            return self._cursor.get_rich_cursor()
        
        a, b = (
            self._typed_chars[:self._cursor.index],
            self._typed_chars[self._cursor.index:],
        )
        if self._cursor.shape == '|':
            return '{}{}{}'.format(
                ''.join(a), self._cursor.get_rich_cursor(), ''.join(b)
            )
        else:
            if not b: b.append(' ')
            b[0] = self._cursor.get_rich_cursor(b[0])
            return '{}{}'.format(''.join(a), ''.join(b))
    
    @property
    def text(self):
        return ''.join(self._typed_chars)
    
    @property
    def text_with_cursor(self):
        if not self._typed_chars:
            return self._cursor.shape
        
        a, b = (
            self._typed_chars[:self._cursor.index],
            self._typed_chars[self._cursor.index:],
        )
        
        if self._cursor.shape == '|':
            return '{}{}{}'.format(
                ''.join(a),
                self._cursor.shape,
                ''.join(b),
            )
        else:
            # warning: the cursor is invisible in this function.
            # suggest using `self.rich_text_with_cursor` instead.
            return '{}{}'.format(
                ''.join(a),
                ''.join(b),
            )


class Cursor:
    """
    references:
        cursor blinking: https://github.com/camgraff/tmux-schmooze/blob/master
            /tmux_schmooze/ui.py
    
    FIXME:
        - if cursor shape is '▉', the blinking effect is invalid.
    """
    index: int  # starts from 0. it indicates the left side of current char.
    shape: str
    _rich_shape: str
    
    def __init__(self, shape='_', blink=True, bold=False):
        """
        args:
            shape: literal['_', '|', '▉']
            blink: bool[True]
                notice: the blinking effect is a little laggy (delay 100~200ms).
            bold: bool[False]
        """
        assert shape in ('_', '|', '▉')
        #   _   underline           default type. green char with underline
        #                           effect.
        #   ▉   block               white text on green background.
        #   |   line                green line between two chars. note this
        #                           shape is special compared to others. it
        #                           takes one additional place to show itself.
        #   note:
        #       - double underline is experimental feature, currently it looks
        #         very ugly... (i think it should be removed from list soon.)
        #       - the line cursor performs not very good in terminal ui.
        #       - underline and block are always your best choice.
        #       - some of the effects are partially rendered in
        #        `TypedChars.rich_text_with_cursor`. it might not be a good
        #         design.
        
        self.index = 0
        self.shape = shape
        
        self._rich_shape = '[{0} {1} {2}]{3}[/]'.format(
            'blink' if blink else '',
            'bold' if bold else '',
            {
                '_': 'u color(36)',  # blue underline
                '|': 'color(36)',  # blue
                '▉': 'color(16) on green',  # grey on green
            }[shape],
            '|' if shape == '|' else '{char}'
            #   about '{char}': see `self.get_rich_cursor`.
        )
        # fix style markup format.
        from re import sub
        self._rich_shape = sub(r'^\[ +', '[', self._rich_shape)
        self._rich_shape = sub(r' +', ' ', self._rich_shape)
        #   before: '[ bold color(36)]|[/]'
        #       after:  '[bold color(36)]|[/]'
        #                ^ remove space after left bracket.
        #   before: '[blink  u color(36)]{}[/]'
        #       after:  '[blink u color(36)]{}[/]'
        #                      ^ merge duplicated spaces.
    
    def activate(self, x: int, text_length: int):
        self.index = min((x, text_length))
    
    def get_rich_cursor(self, char=' '):
        if self.shape == '|':
            return self._rich_shape
        if char != ' ':
            # temporarily cancel blink for visual-friendly.
            return self._rich_shape.format(char=char).replace(
                '[blink ', '[', 1
            )
        else:
            return self._rich_shape.format(char=char)
    
    # movements
    #   return: bool -- True means cursor index changed. False not.
    
    def to_left(self):
        if self.index > 0:
            self.index -= 1
            return True
        else:
            return False
    
    def to_right(self, text_length: int = None):
        if text_length is None:
            self.index += 1
            return True
        if self.index < text_length:
            self.index += 1
            return True
        else:
            return False
    
    def to_start(self) -> bool:
        if self.index != 0:
            self.index = 0
            return True
        else:
            return False
    
    def to_end(self, text_length: int) -> bool:
        if self.index != text_length:
            self.index = text_length
            return True
        else:
            return False
