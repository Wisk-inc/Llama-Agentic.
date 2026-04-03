import os
import sys
import platform
import httpx
from rich.console import Console
from rich.panel import Panel
from rich.columns import Columns
from rich.spinner import Spinner
from rich.live import Live
from rich.text import Text
from config import settings
from ui.theme import get_theme

LLAMA_ASCII = """
      ░░░░
     ░ ██ ░░
    ░ ████ ░
     ░████░
      ████
      █  █
      █  █
    ██████████
"""

def detect_ollama():
    url = settings.get("ollama_url", "http://localhost:11434")
    try:
        response = httpx.get(f"{url}/api/tags", timeout=2)
        if response.status_code == 200:
            models = response.json().get("models", [])
            return True, f"✓ Ollama detected ({len(models)} models available)"
        return False, "✗ Ollama not responding"
    except Exception:
        return False, "✗ Ollama not detected"

def show_splash():
    console = Console()
    theme = get_theme()

    title = Text("Welcome to Llama Agentic v1.0.0", style=f"bold {theme.accent_color}")
    tagline = Text("Your local AI coding agent 🦙", style="italic")

    llama_panel = Panel(
        LLAMA_ASCII,
        title=title,
        subtitle=tagline,
        expand=False,
        border_style=theme.accent_color
    )

    console.print("\n")
    console.print(llama_panel, justify="center")
    console.print("\n" + "─" * console.width + "\n")

    with Live(Spinner("dots", text="Detecting environment..."), refresh_per_second=10) as live:
        ollama_status, ollama_msg = detect_ollama()
        python_ver = f"✓ Python {platform.python_version()}"
        working_dir = f"✓ Working dir: {os.getcwd()}"

        status_text = Text()
        status_text.append(f"{ollama_msg}\n", style=theme.success_color if ollama_status else theme.error_color)
        status_text.append(f"{python_ver}\n", style=theme.success_color)
        status_text.append(f"{working_dir}\n", style=theme.accent_color)

        live.update(status_text)

    console.print("\n" + "─" * console.width + "\n")
