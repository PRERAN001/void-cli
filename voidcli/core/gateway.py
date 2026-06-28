# core/gateway.py

from voidcli.core.task_context import TaskContext
from voidcli.events.task import TaskCreated


class Gateway:
    def __init__(self, session):
        self.session = session

    def receive(self, prompt: str):       

        task = TaskContext(prompt=prompt)
        self.session.tasks[task.task_id] = task

        event = TaskCreated(task.task_id)
        self.session.bus.publish(event)
        return task
