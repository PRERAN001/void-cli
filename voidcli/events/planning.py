from voidcli.events.base import Event


class PlanStepCreated(Event):

    def __init__(self, task_id, step):

        super().__init__(
            event_type="PLAN_STEP_CREATED",
            task_id=task_id,
            payload={
                "step": step
            }
        )