# tools/terminal.py

import subprocess

from voidcli.tools.base import BaseTool


class TerminalTool(BaseTool):

    name = "terminal"

    description = "Execute terminal commands."

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
                        "command": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "command"
                    ]
                }
            }
        }

    def execute(self, command):

        try:

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True
            )

            return (
                result.stdout
                if result.stdout
                else result.stderr
            )

        except Exception as e:

            return str(e)