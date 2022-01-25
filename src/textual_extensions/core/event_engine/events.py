import asyncio
from collections import defaultdict


class EventBus:
    # TODO:
    #   - unsubscribe
    #   - audit and traceback
    #   - async broadcasting
    _events = defaultdict(set)  # dict[str channel, list[callback]]
    
    def subscribe(self, channel, callback):
        self._events[channel].add(callback)
    
    # @new_thread
    def broadcast(self, channel, *args, **kwargs):
        for callback in self._events[channel]:
            callback(*args, **kwargs)


class AsyncEventBus:
    # TODO:
    #   - unsubscribe
    #   - audit and traceback
    #   - async broadcasting
    _events = defaultdict(set)  # dict[str channel, list[callback]]
    _is_running = False
    
    def __init__(self):
        self._queue = asyncio.Queue(maxsize=3)
        # asyncio.run(self._launch_consume_loop())
    
    async def _launch_consume_loop(self):
        await asyncio.create_task(self._consume())
    
    def subscribe(self, channel, callback):
        self._events[channel].add(callback)
    
    # @new_thread
    async def broadcast(self, channel, *args, **kwargs):
        await self._queue.put((channel, args, kwargs))
        if not self._is_running:
            self._is_running = True
            asyncio.run(self._launch_consume_loop())

    async def _consume(self):
        while True:
            if self._queue.empty():
                await asyncio.sleep(1.1)
                # print('queue is empty')
                continue
            channel, args, kwargs = await self._queue.get()
            for callback in self._events[channel]:
                callback(*args, **kwargs)


event_bus = EventBus()
# event_bus = AsyncEventBus()
