# core/registry.py

from voidcli.agents.planner import PlannerAgent
from voidcli.agents.executor import ExecutorAgent
from voidcli.tools.filesystem import FileSystemTool
from voidcli.tools.integrations import IntegrationTool
from voidcli.tools.python import PythonTool
from voidcli.tools.terminal import TerminalTool


class Registry:

    def __init__(self, session):

        self.session = session

        self.agents = []

        self.tools = {}

    # -----------------------------
    # Agents
    # -----------------------------

    def register_default_agents(self):

        self.register_agent(
            PlannerAgent(self.session)
        )

        self.register_agent(
            ExecutorAgent(self.session)
        )

    def register_agent(self, agent):

        self.agents.append(agent)

    def find_agents(self, event):

        return [

            agent

            for agent in self.agents

            if agent.can_handle(event)

        ]

    # -----------------------------
    # Tools
    # -----------------------------

    def register_default_tools(self):

        self.register_tool(
            FileSystemTool()
        )

        self.register_tool(
            TerminalTool()
        )

        self.register_tool(
            PythonTool()
        )

        self.register_tool(
            IntegrationTool()
        )

    def register_tool(self, tool):

        self.tools[tool.name] = tool

    def get_tool(self, name):

        return self.tools.get(name)

    def get_tool_schemas(self):

        return [

            tool.schema

            for tool in self.tools.values()

        ]
