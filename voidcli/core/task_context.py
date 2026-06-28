# core/task_context.py

from dataclasses import dataclass, field
from uuid import uuid4
from datetime import datetime


@dataclass
class TaskContext:

    
    task_id: str = field(default_factory=lambda: str(uuid4()))

    created_at: datetime = field(default_factory=datetime.utcnow)

   
    prompt: str = ""

    status: str = "CREATED"


    plan = None

    current_step = 0

    completed_steps: list = field(default_factory=list)

   
    tool_history: list = field(default_factory=list)

  
    modified_files: list = field(default_factory=list)

    created_files: list = field(default_factory=list)

    deleted_files: list = field(default_factory=list)

    result = None

    metadata: dict = field(default_factory=dict)