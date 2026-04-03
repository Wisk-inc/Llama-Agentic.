import os
from pathlib import Path
from rich.console import Console
from rich.tree import Tree
from rich.text import Text

def list_directory(path: str = ".") -> str:
    path = Path(path)
    if not path.exists():
        return f"Error: Path '{path}' not found."

    if not path.is_dir():
        return f"Error: '{path}' is not a directory."

    ignore_list = {".git", "__pycache__", "node_modules", ".venv", "venv", ".idea", ".vscode"}

    # Try to read .gitignore
    gitignore_path = path / ".gitignore"
    if gitignore_path.exists():
        try:
            with open(gitignore_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        ignore_list.add(line)
        except Exception:
            pass

    tree = Tree(f"[bold blue]{path.absolute()}[/bold blue]")

    def add_to_tree(directory, tree_node):
        try:
            items = sorted(os.listdir(directory))
            for item in items:
                if item in ignore_list:
                    continue

                full_path = os.path.join(directory, item)
                if os.path.isdir(full_path):
                    branch = tree_node.add(f"[bold blue]{item}/[/bold blue]")
                    # For performance, maybe don't recurse too deep
                    # add_to_tree(full_path, branch)
                else:
                    size = os.path.getsize(full_path)
                    size_str = f"{size / 1024:.1f} KB" if size > 1024 else f"{size} B"
                    tree_node.add(f"{item} ({size_str})")
        except Exception as e:
            tree_node.add(f"[red]Error: {str(e)}[/red]")

    add_to_tree(path, tree)

    console = Console(record=True)
    console.print(tree)
    return console.export_text()

TOOL_SPEC = {
    "name": "list_directory",
    "description": "List files and folders in a directory, respecting .gitignore.",
    "parameters": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "The directory to list. Default is current directory."
            }
        }
    }
}
