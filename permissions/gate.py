from rich.console import Console
from rich.panel import Panel
from prompt_toolkit import prompt
from config import settings

def ask_permission(message: str, destructive: bool = False) -> bool:
    if not settings.get("confirm_destructive") and not destructive:
        return True

    console = Console()
    style = "bold red" if destructive else "bold yellow"

    console.print(Panel(message, title="Permission Request", border_style=style))

    while True:
        response = prompt("Confirm action? (y/n): ").lower()
        if response in ['y', 'yes']:
            return True
        if response in ['n', 'no']:
            return False
        console.print("[bold red]Please enter y or n.[/bold red]")

def check_destructive_command(command: str) -> bool:
    destructive_keywords = ['rm -rf', 'sudo', 'format', 'mkfs', 'dd if=']
    for kw in destructive_keywords:
        if kw in command:
            return True
    return False
