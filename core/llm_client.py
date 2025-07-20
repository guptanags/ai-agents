
import json
import os
from litellm import completion
from core.prompt import Prompt


class LLMClient:

    
    def generate_response(self, prompt: Prompt) -> str:
    
        MODEL = os.getenv('LLM_MODEL', 'gemini/gemini-2.5-flash')
        MAX_TOKENS = int(os.getenv('MAX_TOKENS', 60000))
        """Call LLM to get response"""

        messages = prompt.messages
        tools = prompt.tools

        result = None

        if not tools:
            response = completion(
                model=MODEL,
                messages=messages,
                max_tokens=MAX_TOKENS
            )
            result = response.choices[0].message.content
        else:
            response = completion(
                model=MODEL,
                messages=messages,
                tools=tools,
                max_tokens=MAX_TOKENS,
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
