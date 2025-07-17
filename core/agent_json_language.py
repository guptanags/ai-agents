import json
from typing import List

from core.action import Action
from core.action_language import AgentLanguage
from core.environment import Environment
from core.goal import Goal
from core.memory import Memory
from core.prompt import Prompt


class AgentJsonActionLanguage(AgentLanguage):
    # Update: Default system prompt for conversational JSON responses only
    default_system_prompt = {
        "role": "system",
        "content": (
            "You are an autonomous agent. For every user message, respond ONLY with a JSON object in the following format:\n"
            '{"response": "<your reply>"}\n'
            "Do not include any other text or explanation. Always respond in this JSON format."
        )
    }

    def format_actions(self, actions: List[Action]) -> List:
        # Convert actions to a description the LLM can understand
        action_descriptions = [
            {
                "name": action.name,
                "description": action.description,
                "args": action.parameters
            } 
            for action in actions
        ]
        
        return [
            self.default_system_prompt
        ]

    def parse_response(self, response: str) -> dict:
        """Extract and parse the action block"""
        try:
            start_marker = "```action"
            end_marker = "```"
            
            stripped_response = response.strip()
            start_index = stripped_response.find(start_marker)
            end_index = stripped_response.rfind(end_marker)
            json_str = stripped_response[
                start_index + len(start_marker):end_index
            ].strip()
            
            return json.loads(json_str)
        except Exception as e:
            print(f"Failed to parse response: {str(e)}")
            raise e
        
    def construct_prompt(self,
                         actions: List[Action],
                         environment: Environment,
                         goals: List[Goal],
                         memory: Memory) -> Prompt:
        """Build prompt with memory context"""
        # The AgentLanguage decides how to present each component to the LLM
        prompt = []
        
        # Transform goals into instructions
        prompt += self.format_goals(goals)
        
        # Transform available actions into tool descriptions
        prompt += self.format_actions(actions)
        
        # Transform memory into conversation context
        prompt += self.format_memory(memory)
        
        def parse_response(self, json_str):
            print("Raw agent response:", repr(json_str))  # Debug print
            if not json_str or not json_str.strip():
                raise ValueError("Agent response is empty or whitespace.")
            try:
                return json.loads(json_str)
            except Exception as e:
                raise e
        
        return Prompt(messages=prompt)
    
    def format_goals(self, goals: List[Goal]) -> List:
        # Map all goals to a single string that concatenates their description
        # and combine into a single message of type system
        sep = "\n-------------------\n"
        goal_instructions = "\n\n".join([f"{goal.name}:{sep}{goal.description}{sep}" for goal in goals])
        return [
            {"role": "system", "content": goal_instructions}
        ]

    def format_memory(self, memory: Memory) -> List:
        """Generate response from language model"""
        # Map all environment results to a role:user messages
        # Map all assistant messages to a role:assistant messages
        # Map all user messages to a role:user messages
        items = memory.get_memories()
        mapped_items = []
        for item in items:

            content = item.get("content", None)
            if not content:
                content = json.dumps(item, indent=4)

            if item["type"] == "assistant":
                mapped_items.append({"role": "assistant", "content": content})
            elif item["type"] == "environment":
                mapped_items.append({"role": "assistant", "content": content})
            else:
                mapped_items.append({"role": "user", "content": content})

        return mapped_items
