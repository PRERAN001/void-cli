import json

from voidcli.services.integrations import IntegrationManager
from voidcli.tools.base import BaseTool


class IntegrationTool(BaseTool):
    name = "integrations"
    description = "Use configured external integrations such as GitHub, Gmail, Drive, Slack, Notion, Linear, Jira, Discord, Docker, and MongoDB."

    def __init__(self):
        self.manager = IntegrationManager()

    @property
    def schema(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "service": {
                            "type": "string",
                            "description": "Integration key, for example github, gmail, google_drive, slack, notion, linear, jira, discord, docker, mongodb.",
                        },
                        "action": {
                            "type": "string",
                            "description": "Action to run. Use status to check connectivity.",
                        },
                        "args": {
                            "type": "object",
                            "description": "Action-specific arguments.",
                        },
                    },
                    "required": ["service", "action"],
                },
            },
        }

    def execute(self, service, action="status", args=None):
        try:
            result = self.manager.execute(service, action, **(args or {}))
        except Exception as exc:
            result = {
                "ok": False,
                "error": str(exc),
            }
        return json.dumps(result, indent=2, default=str)
