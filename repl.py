import asyncio
import os
import sys
from prompt_toolkit import PromptSession, HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from config import settings
from ui.theme import show_theme_selector, get_theme
from session.session_store import SessionStore, generate_session_id
from session.transcript import TranscriptStore
from providers.setup import setup_provider

class LlamaRepl:
    def __init__(self, agent):
        self.agent = agent
        self.console = Console()
        self.session_id = generate_session_id()
        self.store = SessionStore()
        self.transcript = TranscriptStore()

        self.prompt_session = PromptSession(
            history=FileHistory(os.path.expanduser("~/.llama-agentic/history")),
            auto_suggest=AutoSuggestFromHistory()
        )

    def show_help(self):
        help_text = """
/help       - Show this help message
/theme      - Change TUI theme
/model      - Switch provider/model
/clear      - Clear session transcript
/save       - Save current session
/load <id>  - Load a previous session
/files      - List current files
/cd <path>  - Change working directory
/exit       - Exit Llama Agentic
"""
        theme = get_theme()
        self.console.print(Panel(help_text, title="Available Commands", border_style=theme.accent_color))

    async def run(self):
        theme = get_theme()
        self.console.print(f"[bold {theme.accent_color}]Session started: {self.session_id}[/bold {theme.accent_color}]")
        self.console.print("Type [bold]/help[/bold] for a list of commands.\n")

        while True:
            try:
                provider = settings.get("provider", "ollama")
                model = settings.get("model", "llama3.2")
                cwd = os.getcwd()

                bottom_toolbar = HTML(
                    f'<b>Provider:</b> {provider} | '
                    f'<b>Model:</b> {model} | '
                    f'<b>CWD:</b> {cwd}'
                )

                user_input = await self.prompt_session.prompt_async(
                    HTML('<b>🦙 llama-agentic > </b>'),
                    bottom_toolbar=bottom_toolbar
                )

                if not user_input.strip():
                    continue

                if user_input.startswith('/'):
                    cmd_parts = user_input.split()
                    cmd = cmd_parts[0][1:]
                    args = cmd_parts[1:]

                    if cmd == 'exit':
                        break
                    elif cmd == 'help':
                        self.show_help()
                    elif cmd == 'theme':
                        show_theme_selector()
                    elif cmd == 'model':
                        provider_obj, model_name = await setup_provider()
                        self.agent.provider = provider_obj
                        self.agent.model = model_name
                        self.console.print(f"[{theme.success_color}]Switched to {model_name} via {settings.get('provider')}.[/{theme.success_color}]")
                    elif cmd == 'clear':
                        self.transcript = TranscriptStore()
                        self.agent.transcript = self.transcript
                        self.console.print(f"[{theme.success_color}]Transcript cleared.[/{theme.success_color}]")
                    elif cmd == 'save':
                        path = self.store.save_session(self.session_id, self.transcript.replay())
                        self.console.print(f"[{theme.success_color}]Session saved to: {path}[/{theme.success_color}]")
                    elif cmd == 'load':
                        if args:
                            try:
                                session_data = self.store.load_session(args[0])
                                self.transcript = TranscriptStore()
                                self.transcript.messages = session_data["messages"]
                                self.agent.transcript = self.transcript
                                self.session_id = session_data["session_id"]
                                self.console.print(f"[{theme.success_color}]Loaded session: {self.session_id}[/{theme.success_color}]")
                            except Exception as e:
                                self.console.print(f"[{theme.error_color}]Error loading session: {str(e)}[/{theme.error_color}]")
                        else:
                            sessions = self.store.list_sessions()
                            table = Table(title="Recent Sessions")
                            table.add_column("Session ID")
                            table.add_column("Date")
                            table.add_column("Summary")
                            for s in sessions:
                                table.add_row(s["id"], str(s["timestamp"]), s["summary"])
                            self.console.print(table)
                            self.console.print("Usage: /load <session_id>")
                    elif cmd == 'files':
                        from tools.file_list import list_directory
                        self.console.print(list_directory())
                    elif cmd == 'cd':
                        if args:
                            try:
                                os.chdir(args[0])
                                self.console.print(f"[{theme.success_color}]Changed directory to {os.getcwd()}[/{theme.success_color}]")
                            except Exception as e:
                                self.console.print(f"[{theme.error_color}]Error: {str(e)}[/{theme.error_color}]")
                        else:
                            self.console.print(f"[{theme.error_color}]Usage: /cd <path>[/{theme.error_color}]")
                    else:
                        self.console.print(f"[{theme.error_color}]Unknown command: /{cmd}[/{theme.error_color}]")
                else:
                    await self.agent.run_turn(user_input)

            except KeyboardInterrupt:
                continue
            except EOFError:
                break
            except Exception as e:
                self.console.print(f"[bold {theme.error_color}]Critical Error: {str(e)}[/bold {theme.error_color}]")

        self.console.print(f"\n[bold {theme.accent_color}]Goodbye! 🦙[/bold {theme.accent_color}]")
