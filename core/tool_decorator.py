

import inspect
from typing import get_type_hints

tools = {}
tools_by_tag = {}

def get_tool_metadata(func, tool_name=None, description=None, 
                     parameters_override=None, terminal=False, 
                     tags=None):
    """Extract metadata while ignoring special parameters."""
    signature = inspect.signature(func)
    type_hints = get_type_hints(func)

    args_schema = {
        "type": "object",
        "properties": {},
        "required": []
    }

    for param_name, param in signature.parameters.items():
        # Skip special parameters - agent doesn't need to know about these
        if param_name in ["action_context", "action_agent"] or \
           param_name.startswith("_"):
            continue

        # Add regular parameters to the schema
        param_type = type_hints.get(param_name, str)
        args_schema["properties"][param_name] = {
            "type": "string"  # Simplified for example
        }

        if param.default == param.empty:
            args_schema["required"].append(param_name)

    return {
        "name": tool_name or func.__name__,
        "description": description or func.__doc__,
        "parameters": args_schema,
        "tags": tags or [],
        "terminal": terminal,
        "function": func
    }


def register_tool(tool_name=None, description=None, parameters_override=None, terminal=False, tags=None):
    """
    A decorator to dynamically register a function in the tools dictionary with its parameters, schema, and docstring.

    Parameters:
        tool_name (str, optional): The name of the tool to register. Defaults to the function name.
        description (str, optional): Override for the tool's description. Defaults to the function's docstring.
        parameters_override (dict, optional): Override for the argument schema. Defaults to dynamically inferred schema.
        terminal (bool, optional): Whether the tool is terminal. Defaults to False.
        tags (List[str], optional): List of tags to associate with the tool.

    Returns:
        function: The wrapped function.
    """
    def decorator(func):
        # Use the reusable function to extract metadata
        metadata = get_tool_metadata(
            func=func,
            tool_name=tool_name,
            description=description,
            parameters_override=parameters_override,
            terminal=terminal,
            tags=tags
        )

        # Register the tool in the global dictionary
        tools[metadata["name"]] = {
            "description": metadata["description"],
            "parameters": metadata["parameters"],
            "function": metadata["function"],
            "terminal": metadata["terminal"],
            "tags": metadata["tags"] or []
        }

        for tag in metadata["tags"]:
            if tag not in tools_by_tag:
                tools_by_tag[tag] = []
            tools_by_tag[tag].append(metadata["name"])

        return func
    return decorator