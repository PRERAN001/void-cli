# core/event_bus.py

from collections import deque
class EventBus:
    def __init__(self):
        self.queue = deque()

    def publish(self, event):
        
        self.queue.append(event)

    def consume(self):
        
        if self.queue:
            return self.queue.popleft()

        return None

    def has_events(self):
        return len(self.queue) > 0

    def size(self):
        return len(self.queue)

    def clear(self):
        self.queue.clear()