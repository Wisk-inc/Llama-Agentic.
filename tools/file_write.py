import os
import difflib
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from permissions import gate
from ui.diff_viewer import display_diff

def write_file(path: str, content: str, show_diff: bool = True) -> bool:
    console = Console()

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            old_content = f.readlines()

        new_content = [line + '\n' for line in content.splitlines()]

        if show_diff:
            display_diff(path, old_content, new_content)

            if not gate.ask_permission(f"Apply these changes to {path}?"):
                return False
    else:
        console.print(f"[bold cyan]Creating new file: {path}[/bold cyan]")
        if not gate.ask_permission(f"Create file {path}?"):
            return False

    try:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        console.print(f"[bold green]✓ Successfully wrote {path}.[/bold green]")
        return True
    except Exception as e:
        console.print(f"[bold red]✗ Error writing {path}: {str(e)}[/bold red]")
        return False

TOOL_SPEC = {
    "name": "write_file",
    "description": "Write or update content of a file, showing a diff before applying.",
    "parameters": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "The path to the file."
            },
            "content": {
                "type": "string",
                "description": "The full content to write into the file."
            }
        },
        "required": ["path", "content"]
    }
}
