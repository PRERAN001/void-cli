# agents/executor.py

from voidcli.agents.base import BaseAgent

from voidcli.events.tool import (
    ToolCompleted,
    ToolFailed
)


class ExecutorAgent(BaseAgent):

    name = "executor"

    def can_handle(self, event):

        return event.event_type == "PLAN_STEP_CREATED"

    def handle(self, event):

        task = self.session.tasks[event.task_id]

        step = event.payload["step"]

        tool = self.session.registry.get_tool(
            step["tool"]
        )

        if tool is None:

            return [
                ToolFailed(
                    task.task_id,
                    step["tool"],
                    "Tool not found"
                )
            ]

        try:

            result = tool.execute(
                action=step["action"],
                **step["args"]
            )

            task.completed_steps.append(step)

            task.tool_history.append({

                "tool": step["tool"],

                "action": step["action"],

                "result": result

            })

            return [

                ToolCompleted(

                    task.task_id,

                    step["tool"],

                    result

                )

            ]

        except Exception as e:

            return [

                ToolFailed(

                    task.task_id,

                    step["tool"],

                    str(e)

                )

            ]