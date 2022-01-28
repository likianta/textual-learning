from string import printable

from textual import events
from textual.keys import Keys
from textual.widget import Widget

from .focus_scope import Focusable
from ..core import log


class Input(Widget, Focusable):
    # TODO: features in progress:
    #   - copy, clip and paste
    #   - selection (mouse selection and keyboard selection)
    #   - jump by word (ctrl + left, ctrl + right)
    #   - auto complete (popup or inline prompt text)
    # FIXME:
    #   - rich highlight syntax is laggy (see `Cursor.rich_shape` and
    #    `TypedChars.rich_text_with_cursor`)
    #   - when text is too long to show, the cursor will be out of the visible
    #     zone.
    _focused: bool
    _padding: int
    _placeholder = ''
    _typed_chars: 'TypedChars'
    
    def __init__(
            self, text='', placeholder='', *,
            cursor_bold=False, cursor_shape='_', focus_scope=None, padding=1,
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
            text, cursor_bold=cursor_bold, cursor_shape=cursor_shape
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
        self.gain_focus()
        self._typed_chars.activate(event.x - self._padding)
        self.refresh()
        event.prevent_default()
    
    async def on_key(self, event: events.Key):
        log('key: {}'.format(event.key))
        
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
        
        elif event.key in (Keys.Enter, Keys.Escape):
            # emit('enter', self._text)  # FIXME
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
    
    def gain_focus(self, _notify=True):
        super().gain_focus(_notify)
        self.refresh()
        # self.app.set_focus(self)
    
    def lose_focus(self, _notify=True):
        super().lose_focus(_notify)
        self.refresh()
    
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
    
    def __init__(
            self, text: str = '', *,
            cursor_bold=False, cursor_shape='_'
    ):
        self._cursor = Cursor(cursor_shape, cursor_bold)
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
            return self._cursor.rich_shape
        
        a, b = (
            self._typed_chars[:self._cursor.index],
            self._typed_chars[self._cursor.index:],
        )
        if self._cursor.shape == '|':
            return '{}{}{}'.format(
                ''.join(a),
                self._cursor.rich_shape,
                ''.join(b),
            )
        else:
            if not b:
                b.append(' ')
            if self._cursor.shape == '_':
                # underline
                if b[0] == ' ':
                    b[0] = '[blink u color(36)]{}[/]'.format(b[0])
                else:  # dont blink if cursor is on a visible character.
                    b[0] = '[u color(36)]{}[/]'.format(b[0])
            elif self._cursor.shape == '▉':
                # block
                if b[0] == ' ':
                    b[0] = '[blink on green]{}[/]'.format(b[0])
                else:
                    b[0] = '[default on green]{}[/]'.format(b[0])
            return '{}{}'.format(
                ''.join(a),
                ''.join(b),
            )
    
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
        - the blinking effect is a little laggy (delay 100~300ms) when it is
            activated.
    """
    index: int  # starts from 0. it indicates the left side of current char.
    rich_shape: str
    shape: str
    
    def __init__(self, shape='_', bold=False):
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
        
        if shape == '▉':
            if bold:
                self.rich_shape = '[blink bold on green] [/]'
            else:
                self.rich_shape = '[blink on greed] [/]'
        else:
            if bold:
                self.rich_shape = '[blink bold color(36)]{}[/]'.format(shape)
            else:
                self.rich_shape = '[blink color(36)]{}[/]'.format(shape)
    
    def activate(self, x: int, text_length: int):
        self.index = min((x, text_length))
    
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
