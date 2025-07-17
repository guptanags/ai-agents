from core.json_prompt import prompt_llm_for_json
from core.memory import Memory
from core.tool_decorator import register_tool
from core.action_context import ActionContext

@register_tool()
def call_agent(action_context: ActionContext, 
               agent_name: str, 
               task: str) -> dict:
    """
    Invoke another agent to perform a specific task.
    
    Args:
        action_context: Contains registry of available agents
        agent_name: Name of the agent to call
        task: The task to ask the agent to perform
        
    Returns:
        The result from the invoked agent's final memory
    """
    # Get the agent registry from our context
    agent_registry = action_context.get_agent_registry()
    if not agent_registry:
        raise ValueError("No agent registry found in context")
    
    # Get the agent's run function from the registry
    agent_run = agent_registry.get_agent(agent_name)
    if not agent_run:
        raise ValueError(f"Agent '{agent_name}' not found in registry")
    
    # Create a new memory instance for the invoked agent
    invoked_memory = Memory()
    
    try:
        # Run the agent with the provided task
        result_memory = agent_run(
            user_input=task,
            memory=invoked_memory,
            # Pass through any needed context properties
            action_context_props={
                'auth_token': action_context.get('auth_token'),
                'user_config': action_context.get('user_config'),
                # Don't pass agent_registry to prevent infinite recursion
            }
        )
        
        # Get the last memory item as the result
        if result_memory.items:
            last_memory = result_memory.items[-1]
            return {
                "success": True,
                "agent": agent_name,
                "result": last_memory.get("content", "No result content")
            }
        else:
            return {
                "success": False,
                "error": "Agent failed to run."
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@register_tool()
def call_agent_with_reflection(action_context: ActionContext, 
                             agent_name: str, 
                             task: str) -> dict:
    """Call agent and receive their full thought process."""
    agent_registry = action_context.get_agent_registry()
    agent_run = agent_registry.get_agent(agent_name)
    
    # Create fresh memory for invoked agent
    invoked_memory = Memory()
    
    # Run agent
    result_memory = agent_run(
        user_input=task,
        memory=invoked_memory
    )
    
    # Get the caller's memory
    caller_memory = action_context.get_memory()
    
    # Add all memories from invoked agent to caller
    # although we could leave off the last memory to
    # avoid duplication
    for memory_item in result_memory.items:
        caller_memory.add_memory({
            "type": f"{agent_name}_thought",  # Mark source of memory
            "content": memory_item["content"]
        })
    
    return {
        "result": result_memory.items[-1].get("content", "No result"),
        "memories_added": len(result_memory.items)
    }


@register_tool()
def hand_off_to_agent(action_context: ActionContext, 
                      agent_name: str, 
                      task: str) -> dict:
    """Transfer control to another agent with shared memory."""
    agent_registry = action_context.get_agent_registry()
    agent_run = agent_registry.get_agent(agent_name)
    
    # Get the current memory to hand off
    current_memory = action_context.get_memory()
    
    # Run agent with existing memory
    result_memory = agent_run(
        user_input=task,
        memory=current_memory  # Pass the existing memory
    )
    
    return {
        "result": result_memory.items[-1].get("content", "No result"),
        "memory_id": id(result_memory)
    }

@register_tool(description="Delegate a task to another agent with selected context")
def call_agent_with_selected_context(action_context: ActionContext,
                                   agent_name: str,
                                   task: str) -> dict:
    """Call agent with LLM-selected relevant memories."""
    agent_registry = action_context.get_agent_registry()
    agent_run = agent_registry.get_agent(agent_name)
    
    # Get current memory and add IDs
    current_memory = action_context.get_memory()
    memory_with_ids = []
    for idx, item in enumerate(current_memory.items):
        memory_with_ids.append({
            **item,
            "memory_id": f"mem_{idx}"
        })
    
    # Create schema for memory selection
    selection_schema = {
        "type": "object",
        "properties": {
            "selected_memories": {
                "type": "array",
                "items": {
                    "type": "string",
                    "description": "ID of a memory to include"
                }
            },
            "reasoning": {
                "type": "string",
                "description": "Explanation of why these memories were selected"
            }
        },
        "required": ["selected_memories", "reasoning"]
    }
    
    # Format memories for LLM review
    memory_text = "\n".join([
        f"Memory {m['memory_id']}: {m['content']}" 
        for m in memory_with_ids
    ])
    
    # Ask LLM to select relevant memories
    selection_prompt = f"""Review these memories and select the ones relevant for this task:

Task: {task}

Available Memories:
{memory_text}

Select memories that provide important context or information for this specific task.
Explain your selection process."""

    # Self-prompting magic to find the most relevant memories
    selection = prompt_llm_for_json(
        action_context=action_context,
        schema=selection_schema,
        prompt=selection_prompt
    )
    
    # Create filtered memory from selection
    filtered_memory = Memory()
    selected_ids = set(selection["selected_memories"])
    for item in memory_with_ids:
        if item["memory_id"] in selected_ids:
            # Remove the temporary memory_id before adding
            item_copy = item.copy()
            del item_copy["memory_id"]
            filtered_memory.add_memory(item_copy)
    
    # Run the agent with selected memories
    result_memory = agent_run(
        user_input=task,
        memory=filtered_memory
    )
    
    # Add results and selection reasoning to original memory
    current_memory.add_memory({
        "type": "system",
        "content": f"Memory selection reasoning: {selection['reasoning']}"
    })
    
    for memory_item in result_memory.items:
        current_memory.add_memory(memory_item)
    
    return {
        "result": result_memory.items[-1].get("content", "No result"),
        "shared_memories": len(filtered_memory.items),
        "selection_reasoning": selection["reasoning"]
    }