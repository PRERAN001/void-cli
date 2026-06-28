# tools/base.py

from abc import ABC, abstractmethod


class BaseTool(ABC):
    

    name = ""
    description = ""

    @property
    @abstractmethod
    def schema(self):
        """
        OpenAI/OpenRouter tool schema.
        """
        pass

    @abstractmethod
    def execute(self, **kwargs):
        
        pass