import subprocess
import sys
import tempfile
from pathlib import Path

from voidcli.tools.base import BaseTool


class PythonTool(BaseTool):
    name = "python"
    description = "Execute Python code in a temporary script."

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
                        "code": {
                            "type": "string",
                            "description": "Python source code to run.",
                        }
                    },
                    "required": [
                        "code"
                    ],
                },
            },
        }

    def execute(self, code, action="run"):
        if action != "run":
            return "Unknown action."

        with tempfile.TemporaryDirectory() as temp_dir:
            script_path = Path(temp_dir) / "tool_script.py"
            script_path.write_text(code, encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=120,
            )

        output = result.stdout or ""
        error = result.stderr or ""

        if result.returncode != 0:
            return error or f"Python exited with code {result.returncode}."

        return output or "Python completed successfully."
