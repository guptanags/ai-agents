import json
import os
import time
import traceback
from litellm import completion
from dataclasses import dataclass, field
from typing import List, Callable, Dict, Any

@dataclass
class Prompt:
    messages: List[Dict] = field(default_factory=list)
    tools: List[Dict] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)  # Fixing mutable default issue



