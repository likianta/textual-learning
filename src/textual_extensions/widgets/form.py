from textual.views import DockView

from .focus_scope import FocusScope
from .input import Input
from .label import Label


class Form(DockView, FocusScope):
    
    def __init__(self, fields: dict, field_width=None):
        # params:
        #   fields: dict[str field, tuple[str value, str placeholder]]
        DockView.__init__(self)
        FocusScope.__init__(self)
        self._fields = fields
        self._field_width = field_width or max(map(len, fields.keys())) + 3
    
    async def on_mount(self, event):
        widgets = []
        for field, (value, placeholder) in self._fields.items():
            widgets.append(Field(field, value, placeholder,
                                 field_width=self._field_width))
        await self.dock(
            *widgets, edge='top', size=2
        )
        # await super().on_mount(event)
        event.prevent_default()


class Field(DockView):
    
    def __init__(self, field: str, value='', placeholder: str = '',
                 field_width: int = None, focus_scope=None):
        super().__init__()
        self._field = field
        self._field_width = field_width
        self._focus_scope = focus_scope
        self._placeholder = placeholder
        self._value = value
    
    async def on_mount(self, event):
        await self.dock(Label(self._field + ': ', align='right'), edge='left',
                        size=self._field_width)
        await self.dock(Input(self._value, self._placeholder,
                              focus_scope=self._focus_scope), edge='left')
