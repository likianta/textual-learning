from textual.widget import Widget


class Form(Widget):
    pass


class FieldInput(Widget):
    
    def __init__(self, field, value, placeholder=None, *, field_width=None):
        super().__init__()
        self._field = field
        self._field_width = field_width or len(field)
        self._placeholder = placeholder or ''
        self._value = value
    
    def render(self):
        return '{}{}'.format(
            self.field,
            self.value or self.placeholder,
        )
    
    @property
    def field(self):
        return '{}{}: '.format(
            ' ' * (self._field_width - len(self._field)),
            self._field
        )
    
    @property
    def field_width(self):
        return self._field_width + 3  # 3 for ': '
    
    @property
    def value(self):
        if self._value:
            return '[white on #6B6B6B]{}[/]'.format(self._value)
        else:
            return ''
    
    @property
    def placeholder(self):
        if self._placeholder:
            return '[gray on #6B6B6B]{}[/]'.format(self._placeholder)
        else:
            return ''


class Input(Widget):
    pass
