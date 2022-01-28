class EventBus:
    
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


event_bus = EventBus()
