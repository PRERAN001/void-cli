from voidcli.events.base import Event


class ToolRequested(Event):

    def __init__(self, task_id, tool_name):
        super().__init__(
            event_type="TOOL_REQUESTED",
            task_id=task_id,
            payload={
                "tool": tool_name
            }
        )


class ToolCompleted(Event):

    def __init__(self, task_id, tool_name, result=None):
        super().__init__(
            event_type="TOOL_COMPLETED",
            task_id=task_id,
            payload={
                "tool": tool_name,
                "result": result
            }
        )


class ToolFailed(Event):

    def __init__(self, task_id, tool_name, error):
        super().__init__(
            event_type="TOOL_FAILED",
            task_id=task_id,
            payload={
                "tool": tool_name,
                "error": error
            }
        )
