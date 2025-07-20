import json
import time
import traceback
from core.environment import Environment
from core.action import Action
from core.goal import Goal
from core.memory import Memory
from core.prompt import Prompt
from dataclasses import dataclass, field
from typing import List, Callable, Dict, Any

class AgentLanguage:
    def __init__(self):
        pass

    def construct_prompt(self,
                         actions: List[Action],
                         environment: Environment,
                         goals: List[Goal],
                         memory: Memory) -> Prompt:
        raise NotImplementedError("Subclasses must implement this method")


    def parse_response(self, response: str) -> dict:
        raise NotImplementedError("Subclasses must implement this method")