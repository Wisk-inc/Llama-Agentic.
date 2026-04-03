import difflib
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

def display_diff(path: str, old_content: list[str], new_content: list[str]):
    console = Console()

    diff = difflib.unified_diff(
        old_content,
        new_content,
        fromfile=f"{path} (current)",
        tofile=f"{path} (new)"
    )

    diff_text = Text()
    for line in diff:
        if line.startswith('+'):
            diff_text.append(line, style="green")
        elif line.startswith('-'):
            diff_text.append(line, style="red")
        elif line.startswith('^'):
            diff_text.append(line, style="blue")
        else:
            diff_text.append(line)

    console.print(Panel(diff_text, title=f"Proposed changes to: {path}"))
