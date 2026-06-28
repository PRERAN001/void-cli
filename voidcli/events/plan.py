# events/plan.py

from voidcli.events.base import Event
class PlanCreated(Event):
    def __init__(self, plan: str):
        super().__init__(
            event_type="PLAN_CREATED",
            payload={
                "plan": plan
            }
        )