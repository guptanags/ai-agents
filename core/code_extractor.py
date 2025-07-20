import re
import os

from core.file_operations import write_to_file

def parse_markdown_and_create_structure(markdown_content, output_base_dir="generated_project"):
    """
    Parses a markdown file containing code blocks with filename: and directory: tags,
    creates directories, and writes code to respective files.
    
    Args:
        markdown_content (str): Content of the markdown file
        output_base_dir (str): Base directory where project structure will be created
    
    Returns:
        list: List of created file paths
    """
    # Validate and create base output directory with permission check
    abs_output_base_dir = os.path.abspath(output_base_dir)
    if not os.access(os.path.dirname(abs_output_base_dir) or '.', os.W_OK):
        print(f"Error: No write permission for parent directory of {abs_output_base_dir}. Please choose a writable location.")
        return []
    print(f"Creating project structure in: {abs_output_base_dir}")
    os.makedirs(abs_output_base_dir,mode=0o755, exist_ok=True)
    
    created_files = []
    
    
    
    # Extract code blocks and parse filename and directory tags
    code_block_pattern = r'```(?:\w+)\nfilename: (.+?)\ndirectory: (.+?)\n(.*?)```'
    code_blocks = re.finditer(code_block_pattern, markdown_content, re.DOTALL)
    
    for block in code_blocks:
        filename = block.group(1).strip()
        directory = block.group(2).strip()
        code_content = block.group(3).strip()
        print(f"Found code block for file: {filename} in directory: {directory}")
        # Construct full filepath
        full_dir_path = os.path.join(abs_output_base_dir, directory)
        full_filepath = os.path.join(full_dir_path, filename)
        # Create file if it has a valid extension
        created_files.append(write_to_file(full_filepath, code_content))
       
    if not created_files:
        print("No valid code blocks or project structure found in the markdown")
    
    return created_files

# Example usage
if __name__ == "__main__":
    # Read the markdown content
    try:
        with open('implementation.md', 'r', encoding='utf-8') as f:
            markdown_content = f.read()
    except FileNotFoundError:
        print("Error: implementation.md not found in the current directory")
        exit(1)
    
    # Create project structure and files
    created = parse_markdown_and_create_structure(markdown_content)
    print("\nCreated files:", created)



    