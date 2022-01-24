from lk_lambdex import lambdex
from textual.views import DockView

from .body import BranchListBody
from .popups import NewBranchDialog
from .toolbar import Toolbar
from ..core import log
from ..core import register


class BranchList(DockView):
    
    async def on_mount(self, _):
        await self.dock(
            Toolbar(spacing=2), edge='bottom', size=3
        )
        
        await self.dock(
            BranchListStack(), edge='top'
        )
        
        # await self.dock(
        #     ListBox(
        #         'master',
        #         'dev',
        #         'feature/foo',
        #         'feature/bar',
        #         'release/1.0',
        #         'release/1.1',
        #         'release/1.2',
        #         'release/2.0',
        #     ), edge='top'
        # )


class BranchListStack(DockView):
    _body: BranchListBody
    _new_branch_dialog: NewBranchDialog
    
    def __init__(self):
        super().__init__()
        register('switch_new_branch_dialog', self._switch_new_branch_dialog)
    
    def _switch_new_branch_dialog(self):
        # self._new_branch_dialog.visible = True
        self._new_branch_dialog.visible = not self._new_branch_dialog.visible
    
    async def on_mount(self, event):
        self._body = BranchListBody(
            'master',
            'dev',
            'feature/foo',
            'feature/bar',
            'release/1.0',
            'release/1.1',
            'release/1.2',
            'release/2.0',
        )
        self._new_branch_dialog = NewBranchDialog()
        # self._new_branch_dialog.visible = False
        
        self._new_branch_dialog.finished.connect(
            lambda text: log('finished', text)
        )
        self._new_branch_dialog.finished.connect(
            lambdex('name', """
                self._body.add(name, 0)
                self._body.select(0)
                self._body.refresh(True, True)
            """)
        )
        
        await self.dock(self._body, edge='top')
        await self.dock(
            self._new_branch_dialog, edge='bottom', size=3, z=1
        )
