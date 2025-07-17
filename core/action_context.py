# core/action_context.py

from typing import Dict
import uuid


class ActionContext:
    """
    Context object passed to agent tools and actions.
    Provides access to agent registry, configuration, and other runtime properties.
    """

    def __init__(self, properties: Dict=None):
        self.context_id = str(uuid.uuid4())
        self.properties = properties or {}

    def get(self, key: str, default=None):
        return self.properties.get(key, default)

    def get_memory(self):
        return self.properties.get("memory", None)