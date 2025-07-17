# First, we'll define our tools using decorators
import os
from typing import List
from core.prompt_expert import prompt_expert
from core.action_context import ActionContext
from core.agent import Agent
from core.agent_function_language import AgentFunctionCallingActionLanguage
from core.agent_json_language import AgentJsonActionLanguage
from core.agent_registry import AgentRegistry
from core.environment import Environment
from core.goal import Goal
from core.plan_first_capability import PlanFirstCapability
from core.prompt import generate_response
from core.python_action_registry import PythonActionRegistry
from core.technical_experts import develop_feature
from core.tool_decorator import register_tool

os.environ['GEMINI_API_KEY'] = "AIzaSyBLPAwhM7qGZXdiFUJjPqU0o8wbxSD1OU8"

@register_tool(tags=["file_operations", "read"])
def read_project_file(name: str) -> str:
    """Reads and returns the content of a specified project file.

    Opens the file in read mode and returns its entire contents as a string.
    Raises FileNotFoundError if the file doesn't exist.

    Args:
        name: The name of the file to read

    Returns:
        The contents of the file as a string
    """
    with open(name, "r") as f:
        return f.read()

@register_tool(tags=["file_operations", "list"])
def list_project_files() -> List[str]:
    """Lists all Python files in the current project directory.

    Scans the current directory and returns a sorted list of all files
    that end with '.py'.

    Returns:
        A sorted list of Python filenames
    """
    return sorted([file for file in os.listdir(".")
                    if file.endswith(".py")])

@register_tool(tags=["system"], terminal=True)
def terminate(message: str) -> str:
    """Terminates the agent's execution with a final message.

    Args:
        message: The final message to return before terminating

    Returns:
        The message with a termination note appended
    """
    return f"{message}\nTerminating..."


# Define the agent's goals
goals = [
    Goal(priority=1,
            name="Gather Information",
            description="Read each file in the project in order to build a deep understanding of the project in order to write a README"),
    Goal(priority=1,
            name="Terminate",
            description="Call terminate when done and provide a complete README for the project in the message parameter")
]

# Create an agent instance with tag-filtered actions
agent = Agent(
    goals=goals,
    agent_language=AgentJsonActionLanguage(),
    # The ActionRegistry now automatically loads tools with these tags
    action_registry=PythonActionRegistry(tags=["file_operations", "system"]),
    generate_response=generate_response,
    environment=Environment(),
    capabilities=[
        PlanFirstCapability(track_progress=True)
    ],
)

# Run the agent with user input
# 
# user_input = "List all Python files in this project, read the contents of each file, and use that information to generate a comprehensive README.md that explains the purpose, structure, and usage of the project. After generating the README content, create a new file named README.md in the project root folder with this content. Finally, terminate and display the README content."
# final_memory = agent.run(user_input)
# print(final_memory.get_memories())


# When setting up the system
registry = AgentRegistry()
# registry.register_agent("scheduler_agent", scheduler_agent.run)

# Include registry in action context
action_context = ActionContext({
    'agent_registry': registry,
    "llm": generate_response,

    # Other shared resources...
})

response = develop_feature(action_context,"As a user, I want to develop a new feature that allows users to submit feedback on the application. The feature should include a form for users to enter their feedback, a way to submit it, and a confirmation message after submission. The feedback should be stored in a database for later review by the development team.") 
print(response.__str__())
# You are an autonomous agent. For every action, respond ONLY with a JSON object in the following format:
# {"tool": "<tool_name>", "args": {<arguments>}}
# If you want to terminate, use:
# {"tool": "terminate", "args": {"message": "<your message>"}}
# Do not include any other text or explanation.


