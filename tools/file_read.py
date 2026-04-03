import os
from rich.console import Console

def read_file(path: str) -> str:
    if not os.path.exists(path):
        return f"Error: File '{path}' not found."

    if os.path.isdir(path):
        return f"Error: '{path}' is a directory."

    try:
        with open(path, "rb") as f:
            # Check for binary
            chunk = f.read(1024)
            if b'\x00' in chunk:
                return f"Error: File '{path}' is binary and cannot be displayed."

        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            output = []
            for i, line in enumerate(lines):
                output.append(f"{i+1:4} | {line.rstrip()}")
            return "\n".join(output)

    except Exception as e:
        return f"Error reading file '{path}': {str(e)}"

TOOL_SPEC = {
    "name": "read_file",
    "description": "Read the contents of a text file with line numbers.",
    "parameters": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "The path to the file to read."
            }
        },
        "required": ["path"]
    }
}
