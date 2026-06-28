# events/base.py

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass
class Event:
    

    event_type: str
    task_id: str
    payload: dict = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)