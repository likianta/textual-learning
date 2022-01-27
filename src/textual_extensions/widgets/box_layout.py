"""
the box layout.
    hbox: ...
    vbox: ...
"""
from textual.views import DockView

from .spacing import HSpacing
from .spacing import VSpacing


class Base(DockView):
    
    def __init__(self, *widgets, default_size=1):
        super().__init__()
        self._default_size = default_size
        self._widgets = list(widgets)
    
    def add_widget(self, widget):
        self._widgets.append(widget)
    
    def add_widgets(self, *widgets):
        self._widgets.extend(widgets)
    
    def remove_widget(self, widget):
        self._widgets.remove(widget)
    
    def pop_widget(self, index=None):
        if index is None:
            return self._widgets.pop()
        else:
            return self._widgets.pop(index)


# class HBox(GridView):
#
#     def __init__(self, *widgets):
#         super().__init__()
#         self._widgets = list(widgets)
#
#     async def on_mount(self, event):
#         self.grid.add_column('col', repeat=len(self._widgets))
#         self.grid.add_row('row')
#         self.grid.set_gap(column=1, row=0)
#         self.grid.set_repeat(column=True, row=False)
#         self.grid.place(*self._widgets)
#         # await self.dock(*self._widgets, edge='left')


class HBox(Base):
    
    def __init__(self, *widgets, spacing=1):
        super().__init__(*widgets, default_size=10)
        #   default_size is as known as item width.
        self._spacing = spacing  # suggest 1 or 0.
    
    async def on_mount(self, event):
        if self._spacing:
            for w in self._widgets:
                await self.dock(w, edge='left',
                                size=getattr(w, 'length', self._default_size))
                await self.dock(VSpacing(self._spacing), edge='left',
                                size=self._spacing)
        else:
            for w in self._widgets:
                await self.dock(w, edge='left',
                                size=getattr(w, 'length', self._default_size))
        event.prevent_default()


class VBox(Base):
    
    def __init__(self, *widgets, spacing=0):
        super().__init__(*widgets, default_size=1)
        #   default_size is as known as line height.
        self._spacing = spacing  # suggest 0 or 1.
    
    async def on_mount(self, event):
        if self._spacing:
            for w in self._widgets:
                await self.dock(w, edge='top', size=1)
                await self.dock(
                    HSpacing(self._spacing), edge='top', size=self._spacing
                )
        else:
            await self.dock(*self._widgets, edge='top', size=1)
        # event.prevent_default()
