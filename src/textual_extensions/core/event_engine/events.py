class EventBusA:
    
    def __init__(self):
        from collections import defaultdict
        from concurrent.futures import ThreadPoolExecutor
        self._events = defaultdict(set)  # dict[str channel, set[callback]]
        self._pool = ThreadPoolExecutor(max_workers=3)
    
    def subscribe(self, channel, callback):
        self._events[channel].add(callback)
    
    def broadcast(self, channel, *args, **kwargs):
        self._pool.submit(self._consume, channel, *args, **kwargs)
    
    def _consume(self, channel, *args, **kwargs):
        for callback in self._events[channel]:
            callback(*args, **kwargs)
    
    def close(self):
        self._pool.shutdown()


class EventBusB:
    
    def __init__(self):
        from collections import defaultdict
        self._events = defaultdict(set)
        #   dict[str channel, set[tuple[func callback, bool is_async]]]
    
    def subscribe(self, channel, callback, is_async=False):
        self._events[channel].add((callback, is_async))
    
    async def broadcast(self, channel, *args, **kwargs):
        for (callback, is_async) in self._events[channel]:
            if is_async:
                await callback(*args, **kwargs)
            else:
                callback(*args, **kwargs)


event_bus = EventBusB()
