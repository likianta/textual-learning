from lk_lambdex import lambdex
from rich.panel import Panel
from rich.text import Text
from textual.widget import Widget
from textual.widgets import Placeholder

from .mini_db import db
from ..basic import HBox
from ..branch_list.body import BranchListBody


class BranchDetails(Widget):
    branch_name = 'master'
    
    def __init__(self):
        super().__init__()
        
        BranchListBody.added.connect(lambdex('index, name', """
            db.add_branch(name)
        """))
        BranchListBody.selected.connect(lambdex('index, name', """
            self.branch_name = name
            self.refresh()
        """))
    
    def render(self):
        content = Text(overflow='ignore')
        try:
            branch_data = db.get_branch(self.branch_name)
        except KeyError:
            branch_data = {'name': self.branch_name, 'status': '<not found>'}
        
        for k, v in branch_data.items():
            content.append(f'{k}: {v}\n')
        return Panel(
            content,
            padding=(1, 2),
            title='Branch details',
            title_align='left'
        )


class FieldA(HBox):
    
    def __init__(self, field, value, placeholder=''):
        # log(field, value, placeholder)
        super().__init__(
            Placeholder(),
            Placeholder(),
        )


class Field(Widget):
    
    def __init__(self, field, value, placeholder='', *,
                 field_width=None):
        super().__init__()
        
        # super().__init__(
        #     field + ': ',
        #     '[green on black]{}[/]'.format(value or placeholder)
        # )
        
        # if placeholder:
        #     placeholder = '[gray]{}[/]'.format(placeholder)
        
        self.field = field
        self.value = value
        self.placeholder = placeholder
        
        self._field_width = field_width or len(field)
    
    def render(self):
        return (
                   '{}{}: '.format(
                       ' ' * (self._field_width - len(self.field)),
                       self.field
                   )
               ) + (
                       '[black on light cyan]{}[/]'.format(self.value) or
                       '[gray]{}[/]'.format(self.placeholder)
               )
