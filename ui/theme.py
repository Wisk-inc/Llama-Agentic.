from dataclasses import dataclass
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from prompt_toolkit import prompt
from config import settings

@dataclass
class Theme:
    name: str
    bg_color: str
    fg_color: str
    accent_color: str
    error_color: str
    success_color: str
    code_theme: str

THEMES = {
    "1": Theme("Dark Mode", "black", "white", "cyan", "red", "green", "monokai"),
    "2": Theme("Light Mode", "white", "black", "blue", "red", "green", "one-light"),
    "3": Theme("Dark (Colorblind)", "black", "white", "yellow", "orange", "blue", "monokai"),
    "4": Theme("Light (Colorblind)", "white", "black", "yellow", "orange", "blue", "one-light"),
    "5": Theme("ANSI Only (Dark)", "default", "default", "cyan", "red", "green", "ansi_dark"),
    "6": Theme("ANSI Only (Light)", "default", "default", "blue", "red", "green", "ansi_light"),
}

def get_theme() -> Theme:
    theme_key = settings.get("theme", "1")
    return THEMES.get(theme_key, THEMES["1"])

def show_theme_selector():
    console = Console()
    console.print(Panel("[bold cyan]Llama Agentic Theme Selector[/bold cyan]"))

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Option", style="dim", width=12)
    table.add_column("Theme Name")

    for key, theme in THEMES.items():
        table.add_row(key, theme.name)

    console.print(table)

    code_sample = """def hello_llama():
    print("Welcome to Llama Agentic!")
    return True
"""

    while True:
        choice = prompt("Pick a theme (1-6): ")
        if choice in THEMES:
            theme = THEMES[choice]
            console.print(f"\n[bold]Preview of {theme.name}:[/bold]")
            syntax = Syntax(code_sample, "python", theme=theme.code_theme, line_numbers=True)
            console.print(Panel(syntax, title="Code Preview"))

            confirm = prompt("Apply this theme? (y/n): ")
            if confirm.lower() == 'y':
                settings.set_val("theme", choice)
                console.print(f"[bold {theme.success_color}]Theme updated![/bold {theme.success_color}]")
                break
        else:
            console.print("[bold red]Invalid choice. Try again.[/bold red]")
