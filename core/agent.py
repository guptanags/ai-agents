import json
from typing import Callable, List
from core.action_language import AgentLanguage
from core.action_registry import ActionRegistry
from core.capability import Capability
from core.environment import Environment

from core.goal import Goal
from core.memory import Memory
from core.prompt import Prompt


class Agent:
    def __init__(self,
                 goals: List[Goal],
                 agent_language: AgentLanguage,
                 action_registry: ActionRegistry,
                 generate_response: Callable[[Prompt], str],
                 environment: Environment,
                 capabilities: List[Capability] = [],
                 max_iterations: int = 10,
                 max_duration_seconds: int = 180):
        """
        Initialize an agent with its core GAME components and capabilities.
        
        Goals, Actions, Memory, and Environment (GAME) form the core of the agent,
        while capabilities provide ways to extend and modify the agent's behavior.
        
        Args:
            goals: What the agent aims to achieve
            agent_language: How the agent formats and parses LLM interactions
            action_registry: Available tools the agent can use
            generate_response: Function to call the LLM
            environment: Manages tool execution and results
            capabilities: List of capabilities that extend agent behavior
            max_iterations: Maximum number of action loops
            max_duration_seconds: Maximum runtime in seconds
        """
        self.goals = goals
        self.generate_response = generate_response
        self.agent_language = agent_language
        self.actions = action_registry
        self.environment = environment
        self.capabilities = capabilities or []
        self.max_iterations = max_iterations
        self.max_duration_seconds = max_duration_seconds

        
    def construct_prompt(self, goals: List[Goal], memory: Memory, actions: ActionRegistry):
        """Build prompt with memory context"""
        return self.agent_language.construct_prompt(
            actions=actions.get_actions(),
            environment=self.environment,
            goals=goals,
            memory=memory
        )

    def get_action(self, response):
        """
        Parse the agent's response and return the action and invocation.
        Handles both tool-based and conversational (no-tool) modes.
        """
        invocation = self.agent_language.parse_response(response)

        # If the response is in conversational mode (no tools), just return the response
        if "tool" not in invocation:
            # No tool requested, treat as conversational response
            return None, invocation

        # Otherwise, proceed as before for tool-based invocation
        action = self.actions.get_action(invocation["tool"])
        return action, invocation

    def should_terminate(self, response: str) -> bool:
        action_def, _ = self.get_action(response)
        return action_def.terminal

    def set_current_task(self, memory: Memory, task: str):
        memory.add_memory({"type": "user", "content": task})

    def update_memory(self, memory: Memory, response: str, result: dict):
        """
        Update memory with the agent's decision and the environment's response.
        """
        new_memories = [
            {"type": "assistant", "content": response},
            {"type": "environment", "content": json.dumps(result)}
        ]
        for m in new_memories:
            memory.add_memory(m)

    def prompt_llm_for_action(self, full_prompt: Prompt) -> str:
        response = self.generate_response(full_prompt)
        return response

    def run(self, user_input: str, memory=None, max_iterations: int = 50) -> Memory:
        """
        Execute the GAME loop for this agent with a maximum iteration limit.
        """
        memory = memory or Memory()
        self.set_current_task(memory, user_input)

        for _ in range(max_iterations):
            # Construct a prompt that includes the Goals, Actions, and the current Memory
            prompt = self.construct_prompt(self.goals, memory, self.actions)

            print("Agent thinking...")
            # Generate a response from the agent
            response = self.prompt_llm_for_action(prompt)
            print(f"Agent Decision: {response}")

            # Determine which action the agent wants to execute
            action, invocation = self.get_action(response)

            # If no action (conversational mode), just store the response and break
            if action is None:
                print(f"Agent Response: {invocation.get('response')}")
                self.update_memory(memory, response, {"tool_executed": False, "result": invocation.get("response")})
                break

            # Execute the action in the environment
            result = self.environment.execute_action(action, invocation.get("args", {}))
            print(f"Action Result: {result}")

            # Update the agent's memory with information about what happened
            self.update_memory(memory, response, result)

            # Check if the agent has decided to terminate
            if self.should_terminate(response):
                break

        return memory