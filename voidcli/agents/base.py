# agents/base.py

from abc import ABC, abstractmethod


class BaseAgent(ABC):
    

    name = "base"

    def __init__(self, session):
        self.session = session

    @abstractmethod
    def can_handle(self, event) -> bool:
        
        pass

    @abstractmethod
    def handle(self, event):
       
        pass