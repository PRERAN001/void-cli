from voidcli.events.base import Event


class TaskCreated(Event):

    def __init__(self, task_id: str):
        super().__init__(
            event_type="TASK_CREATED",
            task_id=task_id
        )


class TaskCompleted(Event):

    def __init__(self, task_id: str):
        super().__init__(
            event_type="TASK_COMPLETED",
            task_id=task_id
        )