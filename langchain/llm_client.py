
import json
import os
from litellm import completion


class LLMClient:

    
    def generate_response(self, prompt: str) -> str:
    
        MODEL = os.getenv('LLM_MODEL', 'gemini/gemini-2.5-flash')
        MAX_TOKENS = int(os.getenv('MAX_TOKENS', 60000))
        """Call LLM to get response"""

        

        result = None

        response = completion(
            model=MODEL,
            messages=prompt,
            max_tokens=MAX_TOKENS
        )
        result = response.choices[0].message.content
    

        
        

        return result
