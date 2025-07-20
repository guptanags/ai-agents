# First, we'll define our tools using decorators
import os
from typing import List
from core.agent_text_language import AgentTextActionLanguage
from core.llm_client import LLMClient
from core.prompt_expert import prompt_expert
from core.action_context import ActionContext
from core.agent import Agent
from core.agent_function_language import AgentFunctionCallingActionLanguage
from core.agent_json_language import AgentJsonActionLanguage
from core.agent_registry import AgentRegistry
from core.environment import Environment
from core.goal import Goal
from core.plan_first_capability import PlanFirstCapability
from core.python_action_registry import PythonActionRegistry
from core.technical_experts import develop_feature
from core.tool_decorator import register_tool
from dotenv import load_dotenv


load_dotenv()

os.environ['GEMINI_API_KEY'] = os.getenv('API_KEY')

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
    name="Implement requested feature including detailed requirements, architecture, code, tests and documentation" ,
    description="Implement requested feature including detailed requirements, architecture, code, tests and documentation"),
   
    Goal(priority=1,
            name="Terminate",
            description="Call terminate when done and provide a complete feature development for the project in the message parameter")
]

registry = AgentRegistry()
llm_client = LLMClient()

action_context = ActionContext({
    'agent_registry': registry,
    "llm": llm_client.generate_response,

    # Other shared resources...
})

# Create an agent instance with tag-filtered actions
developer_agent = Agent(
    goals=goals,
    agent_language=AgentFunctionCallingActionLanguage(),
    # The ActionRegistry now automatically loads tools with these tags
    action_registry=PythonActionRegistry(tags=["system", "feature_development"]),
    generate_response=llm_client.generate_response,
    environment=Environment(),
   
    
)

# Run the agent with user input
# capabilities=[ PlanFirstCapability(track_progress=True) ],
user_input = "I want to develop a new feature that allows users to submit feedback on the application. The feature should include a form for users to enter their feedback, a way to submit it, and a confirmation message after submission. The feedback should be stored in a database for later review by the development team."
final_memory = developer_agent.run(user_input)



# When setting up the system

# registry.register_agent("feature developer", agent.run)

# Include registry in action context

# response = develop_feature(action_context,"As a user, I want to develop a new feature that allows users to submit feedback on the application. The feature should include a form for users to enter their feedback, a way to submit it, and a confirmation message after submission. The feedback should be stored in a database for later review by the development team.") 
# print(response.__str__())
# You are an autonomous agent. For every action, respond ONLY with a JSON object in the following format:
# {"tool": "<tool_name>", "args": {<arguments>}}
# If you want to terminate, use:
# {"tool": "terminate", "args": {"message": "<your message>"}}
# Do not include any other text or explanation.


