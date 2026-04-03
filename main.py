import asyncio
import os
import sys
from rich.console import Console
from ui.splash import show_splash
from config import settings
from providers.ollama_provider import OllamaProvider
from providers.openrouter_provider import OpenRouterProvider
from providers.anthropic_provider import AnthropicProvider
from providers.gemini_provider import GeminiProvider
from providers.setup import setup_provider
from agent import LlamaAgent
from repl import LlamaRepl
from session.transcript import TranscriptStore

async def async_main():
    show_splash()

    provider_name = settings.get("provider")
    model_name = settings.get("model")

    if not provider_name or provider_name == "ollama":
        ollama = OllamaProvider()
        if not ollama.is_running() or not ollama.list_models():
             provider, model = await setup_provider()
        else:
             provider = ollama
             model = model_name or (ollama.list_models()[0] if ollama.list_models() else None)
    else:
        if provider_name == "openrouter":
            provider = OpenRouterProvider()
        elif provider_name == "anthropic":
            provider = AnthropicProvider()
        elif provider_name == "gemini":
            provider = GeminiProvider()
        else:
            provider = OllamaProvider()
        model = model_name

    transcript = TranscriptStore()
    agent = LlamaAgent(provider, model, transcript)

    repl = LlamaRepl(agent)
    await repl.run()

def main():
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
