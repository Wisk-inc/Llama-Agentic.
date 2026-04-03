import os
import re
from rich.console import Console
from rich.panel import Panel

def code_search(pattern: str, path: str = ".") -> str:
    console = Console()
    results = []

    try:
        regex = re.compile(pattern)
    except re.error as e:
        return f"Error: Invalid regex pattern: {str(e)}"

    ignore_list = {".git", "__pycache__", "node_modules", ".venv", "venv"}

    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in ignore_list]

        for file in files:
            full_path = os.path.join(root, file)
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    for i, line in enumerate(f):
                        if regex.search(line):
                            results.append(f"{full_path}:{i+1}: {line.strip()}")
            except (UnicodeDecodeError, PermissionError):
                continue

    if not results:
        return f"No matches found for pattern '{pattern}'."

    return "\n".join(results)

TOOL_SPEC = {
    "name": "code_search",
    "description": "Search for a regex pattern in files within a directory.",
    "parameters": {
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "description": "The regex pattern to search for."
            },
            "path": {
                "type": "string",
                "description": "The directory to search in. Default is current directory."
            }
        },
        "required": ["pattern"]
    }
}
