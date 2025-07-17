import json
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


def generate_response(prompt: Prompt) -> str:
    """Call LLM to get response"""

    messages = prompt.messages
    tools = prompt.tools

    result = None

    if not tools:
        response = completion(
            model="gemini/gemini-2.0-flash",
            messages=messages,
            max_tokens=1024
        )
        result = response.choices[0].message.content
    else:
        response = completion(
            model="gemini/gemini-2.0-flash",
            messages=messages,
            tools=tools,
            max_tokens=1024
        )

        if response.choices[0].message.tool_calls:
            tool = response.choices[0].message.tool_calls[0]
            result = {
                "tool": tool.function.name,
                "args": json.loads(tool.function.arguments),
            }
            result = json.dumps(result)
        else:
            result = response.choices[0].message.content


    return result