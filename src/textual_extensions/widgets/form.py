from textual.keys import Keys
from textual.views import DockView

from .focus_scope import FocusScope
from .input import Input
from .label import Label


class Form(DockView, FocusScope):
    
    def __init__(self, fields: dict, field_width=None):
        # params:
        #   fields: dict[str field, tuple[str value, str placeholder]]
        super().__init__()
        FocusScope.__init__(self)
        
        self._widgets = {}  # dict[str field, Field]
        field_width = field_width or max(map(len, fields.keys())) + 3
        for field, (value, placeholder) in fields.items():
            self._widgets[field] = Field(field, value, placeholder,
                                         field_width=field_width,
                                         focus_scope=self)
            
    async def on_mount(self, event):
        await self.dock(*self._widgets.values(), edge='top', size=2)
        
    def update_data(self, data: dict):
        for field, value in data.items():
            self._widgets[field].update_value(value)


class Field(DockView):
    
    def __init__(self, field: str, value='', placeholder: str = '',
                 field_width: int = None, focus_scope: FocusScope = None):
        super().__init__()
        self._field = field
        self._field_width = field_width
        self._focus_scope = focus_scope
        assert self._focus_scope
        self._input = None
        self._placeholder = placeholder
        self._value = value
    
    async def on_mount(self, event):
        await self.dock(Label(self._field + ': ', align='right'), edge='left',
                        size=self._field_width)
        await self.dock(x := Input(self._value, self._placeholder,
                                   focus_scope=self._focus_scope), edge='left')
        self._input = x

    # async def on_key(self, event):
    #     if event.key == Keys.Tab:
    #         pass

    def update_value(self, value):
        self._value = value
        self._input.set_text(value)
