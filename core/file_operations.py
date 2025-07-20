import os
from typing import List
from core.tool_decorator import register_tool
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

OUTPUT_DIR = os.getenv("OUTPUT_DIR", ".")  # Default to current directory if not set

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


@register_tool(tags=["file_operations", "write"])
def write_to_file(name: str, content: str) -> str:
    """Writes content to a specified file in the OUTPUT_DIR."""

    filepath = os.path.normpath(os.path.join(OUTPUT_DIR, name))
    print(f"Attempting to create: {filepath}")  # Debug output

    parent_dir = os.path.dirname(filepath) or '.'
    # Create parent directory if it doesn't exist
    os.makedirs(parent_dir, mode=0o755, exist_ok=True)

    # Check if parent directory is writable AFTER creation
    if not os.access(parent_dir, os.W_OK):
        print(f"Permission denied: Cannot write to {parent_dir}")
        return

    with open(filepath, "w") as f:
        f.write(content)
    print(f"File '{filepath}' written successfully.")  # Debug print
    return filepath
    

#