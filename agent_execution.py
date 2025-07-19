# First, we'll define our tools using decorators
import os
from typing import List
from core.agent_text_language import AgentTextActionLanguage
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

@register_tool(tags=["file_operations", "write"])
def write_project_file(name: str, content: str) -> str:
    """Writes content to a specified project file."""
    try:
        with open(name, "w") as f:
            f.write(content)
        print(f"File '{name}' written successfully.")  # Debug print
        return f"File '{name}' written successfully."
    except Exception as e:
        print(f"Error writing file '{name}': {e}")
        return f"Error writing file '{name}': {e}"


# Define the agent's goals
goals = [
    Goal(priority=1,
            name="Detailed Requirements",
            description="create detailed requirements and write requirements to a file"),
    Goal(priority=1,
    name="Prepare Architecture",
    description="Design architecture and write to file"),
    Goal(priority=1,
    name="Develop Feature",
    description="Develop code and write each component to a new file"),
    Goal(priority=1,
    name="Prepare Test Cases",
    description="Prepare test cases and write the output to a corrsponding file"),
    Goal(priority=1,
    name="Prepare Documentation",
    description="Prepare documentatio and write the output to a corrsponding file"),
    Goal(priority=1,
            name="Terminate",
            description="Call terminate when done and provide a complete feature development for the project in the message parameter")
]

registry = AgentRegistry()

action_context = ActionContext({
    'agent_registry': registry,
    "llm": generate_response,

    # Other shared resources...
})

# Create an agent instance with tag-filtered actions
agent = Agent(
    goals=goals,
    agent_language=AgentJsonActionLanguage(),
    # The ActionRegistry now automatically loads tools with these tags
    action_registry=PythonActionRegistry(tags=["file_operations", "system", "feature_development", "architecture", "requirements", "tests", "documentation"]),
    generate_response=generate_response,
    environment=Environment(),
   
    
)

# Run the agent with user input
# capabilities=[ PlanFirstCapability(track_progress=True) ],
user_input = "I want to develop a new feature that allows users to submit feedback on the application. The feature should include a form for users to enter their feedback, a way to submit it, and a confirmation message after submission. The feedback should be stored in a database for later review by the development team."
final_memory = agent.run(user_input)
print(final_memory.get_memories())


# When setting up the system

registry.register_agent("feature developer", agent.run)

# Include registry in action context

# response = develop_feature(action_context,"As a user, I want to develop a new feature that allows users to submit feedback on the application. The feature should include a form for users to enter their feedback, a way to submit it, and a confirmation message after submission. The feedback should be stored in a database for later review by the development team.") 
# print(response.__str__())
# You are an autonomous agent. For every action, respond ONLY with a JSON object in the following format:
# {"tool": "<tool_name>", "args": {<arguments>}}
# If you want to terminate, use:
# {"tool": "terminate", "args": {"message": "<your message>"}}
# Do not include any other text or explanation.


