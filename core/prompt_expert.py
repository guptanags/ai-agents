from core.action_context import ActionContext
from core.llm_client import LLMClient
from core.prompt import Prompt
from core.tool_decorator import register_tool


@register_tool()
def prompt_expert( description_of_expert: str, prompt: str) -> str:
    """
    Generate a response from an expert persona.
    
    The expert's background and specialization should be thoroughly described to ensure
    responses align with their expertise. The prompt should be focused on topics within
    their domain of knowledge.
    
    Args:
        description_of_expert: Detailed description of the expert's background and expertise
        prompt: The specific question or task for the expert
        
    Returns:
        The expert's response
    """
    
    
    prompt = Prompt(messages=[
        {"role": "system", 
         "content": f"Act as the following expert and respond accordingly: {description_of_expert}"},
        {"role": "user", "content": prompt}
    ])
    llm_client = LLMClient()
    response = llm_client.generate_response(prompt)
    return response