from ..basic import ListBox
from ..core import signal


class BranchListBody(ListBox):
    added = signal(int, str)
    selected = signal(int, str)
    
    def __init__(self, *branch_names):
        super().__init__(*branch_names, init_index=0)
        if branch_names:
            self.selected.emit(0, branch_names[0])
