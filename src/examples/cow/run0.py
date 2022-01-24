from textual.app import App

from components import *

logger = ...


class CowProject(App):
    
    async def on_mount(self):
        await self.view.dock(Header(), edge='top', size=10)
        
        global logger
        # await self.view.dock(logger, edge='bottom', size=3)
        await self.view.dock((logger := Logger(content_height=1)),
                             edge='bottom', size=3)
        # test1.logger = x
        
        await self.view.dock(BranchList(), edge='left', size=30)
        # await self.view.dock(Placeholder(), edge='left', size=40)
        
        # await self.view.dock(Placeholder(), edge='right')
        await self.view.dock(BranchDetails(), edge='right')
        # await self.view.dock(*BranchDetails.test(), Placeholder(), edge='right')


CowProject.run(log="textual.log")
