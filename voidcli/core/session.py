# core/session.py

from voidcli.services.memory import Memory
from voidcli.services.llmcall import LLMClient
from voidcli.core.event_bus import EventBus


SYSTEM_PROMPT = """
You are an autonomous developer assistant.

Always use tools when necessary.

Never pretend to execute tools.
"""


class Session:

    def __init__(self):

        self.memory = Memory(SYSTEM_PROMPT)

        self.llm = LLMClient()

        self.bus = EventBus()

        self.tasks = {}

        self.cwd = None

        self.active_task = None

        self.active_agent = None

        self.state = {}

    def set(self, key, value):
        self.state[key] = value

    def get(self, key, default=None):
        return self.state.get(key, default)
