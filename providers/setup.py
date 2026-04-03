import asyncio
from rich.console import Console
from rich.panel import Panel
from prompt_toolkit import prompt
from config import settings
from providers.ollama_provider import OllamaProvider
from providers.openrouter_provider import OpenRouterProvider
from providers.anthropic_provider import AnthropicProvider
from providers.gemini_provider import GeminiProvider

async def setup_provider():
    console = Console()
    console.print(Panel("[bold cyan]AI Provider Setup Flow[/bold cyan]"))

    options = [
        "1. Ollama (local, free) - auto-detected if running",
        "2. OpenRouter (API key required)",
        "3. Anthropic Claude (API key required)",
        "4. Google Gemini (API key required)"
    ]

    for opt in options:
        console.print(opt)

    while True:
        choice = prompt("Choose your AI provider (1-4): ")
        if choice == '1':
            ollama = OllamaProvider()
            if ollama.is_running():
                models = ollama.list_models()
                if models:
                    console.print("[green]✓ Detected local models:[/green]")
                    for i, m in enumerate(models):
                        console.print(f"{i+1}. {m}")

                    m_choice = prompt("Pick a model (1-{}): ".format(len(models)))
                    try:
                        idx = int(m_choice) - 1
                        if 0 <= idx < len(models):
                            settings.set_val("provider", "ollama")
                            settings.set_val("model", models[idx])
                            return OllamaProvider(), models[idx]
                    except ValueError:
                        pass
                else:
                    console.print("[yellow]Ollama running but no models found. Please run 'ollama run llama3.2' first.[/yellow]")
            else:
                console.print("[red]Ollama not detected at localhost:11434.[/red]")

        elif choice == '2':
            api_key = prompt("Enter OpenRouter API Key (masked): ", is_password=True)
            api_keys = settings.get("api_keys", {})
            api_keys["openrouter"] = api_key
            settings.set_val("api_keys", api_keys)
            settings.set_val("provider", "openrouter")

            provider = OpenRouterProvider(api_key)
            models = await provider.list_models()
            for i, m in enumerate(models):
                console.print(f"{i+1}. {m}")
            m_choice = prompt("Pick a model (1-{}): ".format(len(models)))
            try:
                idx = int(m_choice) - 1
                if 0 <= idx < len(models):
                    settings.set_val("model", models[idx])
                    return provider, models[idx]
            except ValueError:
                pass

        elif choice == '3':
            api_key = prompt("Enter Anthropic API Key (masked): ", is_password=True)
            api_keys = settings.get("api_keys", {})
            api_keys["anthropic"] = api_key
            settings.set_val("api_keys", api_keys)
            settings.set_val("provider", "anthropic")

            provider = AnthropicProvider(api_key)
            models = await provider.list_models()
            for i, m in enumerate(models):
                console.print(f"{i+1}. {m}")
            m_choice = prompt("Pick a model (1-{}): ".format(len(models)))
            try:
                idx = int(m_choice) - 1
                if 0 <= idx < len(models):
                    settings.set_val("model", models[idx])
                    return provider, models[idx]
            except ValueError:
                pass

        elif choice == '4':
            api_key = prompt("Enter Gemini API Key (masked): ", is_password=True)
            api_keys = settings.get("api_keys", {})
            api_keys["gemini"] = api_key
            settings.set_val("api_keys", api_keys)
            settings.set_val("provider", "gemini")

            provider = GeminiProvider(api_key)
            models = await provider.list_models()
            for i, m in enumerate(models):
                console.print(f"{i+1}. {m}")
            m_choice = prompt("Pick a model (1-{}): ".format(len(models)))
            try:
                idx = int(m_choice) - 1
                if 0 <= idx < len(models):
                    settings.set_val("model", models[idx])
                    return provider, models[idx]
            except ValueError:
                pass

        console.print("[bold red]Invalid choice or error. Try again.[/bold red]")
