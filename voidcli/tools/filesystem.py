# tools/filesystem.py

from pathlib import Path
from voidcli.tools.base import BaseTool


class FileSystemTool(BaseTool):

    name = "filesystem"

    description = "Read and write files on disk."

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
                        "action": {
                            "type": "string",
                            "enum": [
                                "read",
                                "write",
                                "list",
                                "mkdir",
                                "delete"
                            ]
                        },
                        "path": {
                            "type": "string"
                        },
                        "content": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "action",
                        "path"
                    ]
                }
            }
        }

    def execute(self, action, path, content=""):

        path = Path(path)

        try:

            if action == "read":

                return path.read_text()

            elif action == "write":

                path.write_text(content)

                return f"{path} written successfully."

            elif action == "list":

                if not path.exists():
                    return "Directory does not exist."

                return "\n".join(
                    file.name
                    for file in path.iterdir()
                )

            elif action == "mkdir":

                path.mkdir(
                    parents=True,
                    exist_ok=True
                )

                return f"{path} created."

            elif action == "delete":

                path.unlink()

                return f"{path} deleted."

            return "Unknown action."

        except Exception as e:

            return str(e)