# agents/planner.py

import json
import re

from voidcli.agents.base import BaseAgent
from voidcli.events.planning import PlanStepCreated
from voidcli.events.task import TaskCompleted


SYSTEM_PROMPT = """
You are the planning agent.

You MUST return ONLY JSON.

Schema:

{
    "done": false,
    "step": {
        "title": "",
        "tool": "",
        "action": "",
        "args": {}
    }
}

If the task is complete:

{
    "done": true
}
"""


class PlannerAgent(BaseAgent):

    name = "planner"

    def can_handle(self, event):

        return event.event_type in (
            "TASK_CREATED",
            "TOOL_COMPLETED"
        )

    def handle(self, event):

        task = self.session.tasks[event.task_id]

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

        messages.append({
            "role": "user",
            "content": f"""
Current Task:

{task.prompt}

Completed Steps:

{task.completed_steps}

Tool History:

{task.tool_history}

Generate ONLY the next step.
"""
        })

        response = self.session.llm.chat(messages)

        content = response.get("content", "")

        try:
            data = self._parse_json(content)
        except json.JSONDecodeError:
            task.result = content
            return [
                TaskCompleted(task.task_id)
            ]

        if data["done"]:

            return [
                TaskCompleted(task.task_id)
            ]

        return [
            PlanStepCreated(
                task.task_id,
                data["step"]
            )
        ]

    def _parse_json(self, content):
        content = content.strip()

        if content.startswith("```"):
            content = re.sub(r"^```(?:json)?", "", content, flags=re.IGNORECASE).strip()
            content = re.sub(r"```$", "", content).strip()

        return json.loads(content)
