import json
import asyncio
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from prompt_toolkit import PromptSession, HTML
from tools import file_read, file_write, bash_exec, file_list, code_search

class LlamaAgent:
    def __init__(self, provider, model: str, transcript: Any):
        self.provider = provider
        self.model = model
        self.transcript = transcript
        self.tools = {
            "read_file": file_read,
            "write_file": file_write,
            "bash": bash_exec,
            "list_directory": file_list,
            "code_search": code_search
        }
        self.console = Console()
        self.prompt_session = PromptSession()

    def get_tool_specs(self) -> List[Dict[str, Any]]:
        # Map our tool specs to the native provider format
        return [
            {"type": "function", "function": file_read.TOOL_SPEC},
            {"type": "function", "function": file_write.TOOL_SPEC},
            {"type": "function", "function": bash_exec.TOOL_SPEC},
            {"type": "function", "function": file_list.TOOL_SPEC},
            {"type": "function", "function": code_search.TOOL_SPEC}
        ]

    def _get_history(self) -> List[Dict[str, Any]]:
        history = []
        for msg in self.transcript.replay():
            m = {
                "role": msg["role"],
                "content": msg["content"] or ""
            }
            if msg.get("tool_calls"):
                m["tool_calls"] = msg["tool_calls"]
            if msg.get("tool_results"):
                # Handle tool results as separate messages if needed by the provider
                pass
            history.append(m)
        return history

    async def run_turn(self, user_message: str):
        self.transcript.append("user", user_message)

        plan = await self.plan(user_message)
        if not plan:
            return

        await self.execute(plan)

    async def plan(self, user_message: str) -> Optional[List[str]]:
        history = self._get_history()

        planning_prompt = f"""You are a helpful AI coding assistant.
Based on the current conversation, create a step-by-step plan to solve the user's request.
Respond with ONLY a numbered list of steps, no extra text.
Available tools: read_file, write_file, bash, list_directory, code_search
"""
        messages = [{"role": "system", "content": planning_prompt}] + history

        with self.console.status("[bold cyan]📋 Creating plan...", spinner="dots"):
            response = ""
            async for chunk in self.provider.chat(self.model, messages, stream=True):
                if "message" in chunk and "content" in chunk["message"]:
                    response += chunk["message"]["content"]
                elif "choices" in chunk and "delta" in chunk["choices"][0] and "content" in chunk["choices"][0]["delta"]:
                    response += chunk["choices"][0]["delta"]["content"]

        self.console.print(Panel(response, title="📋 Plan", border_style="cyan"))

        confirm = await self.prompt_session.prompt_async(HTML("<b>Proceed with this plan? (y/n/edit): </b>"))
        confirm = confirm.lower()
        if confirm == 'y':
            return [line.strip() for line in response.splitlines() if line.strip()]
        elif confirm == 'edit':
            edited_plan = await self.prompt_session.prompt_async(HTML("<b>Enter your modified plan: </b>"))
            return [line.strip() for line in edited_plan.splitlines() if line.strip()]
        else:
            self.console.print("[yellow]Plan aborted.[/yellow]")
            return None

    async def execute(self, plan: List[str]):
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console,
            transient=True
        ) as progress:
            task_id = progress.add_task("Executing steps...", total=len(plan))

            for i, step in enumerate(plan):
                progress.update(task_id, description=f"⚡ Step {i+1}/{len(plan)}: {step}")

                result = await self.execute_step(step)

                if result is None:
                    action = await self.prompt_session.prompt_async(HTML(f"<b>Step {i+1} failed. Action? (retry/skip/abort): </b>"))
                    if action.lower() == 'retry':
                        await self.execute_step(step)
                    elif action.lower() == 'abort':
                        break

                progress.advance(task_id)

        self.console.print("[bold green]✓ Execution complete.[/bold green]")

    async def execute_step(self, step: str):
        history = self._get_history()
        tool_specs = self.get_tool_specs()

        messages = history + [{"role": "user", "content": f"Execute this step of the plan: {step}"}]

        response_content = ""
        tool_calls = []

        with self.console.status(f"[bold cyan]⚡ Executing: {step}", spinner="dots"):
            async for chunk in self.provider.chat(self.model, messages, tools=tool_specs, stream=False):
                # Handle non-streaming response for tool calls (Ollama/OpenAI)
                if "message" in chunk:
                    msg = chunk["message"]
                    response_content = msg.get("content", "")
                    tool_calls = msg.get("tool_calls", [])
                elif "choices" in chunk:
                    msg = chunk["choices"][0]["message"]
                    response_content = msg.get("content", "")
                    tool_calls = msg.get("tool_calls", [])

        if not tool_calls:
            # Fallback to manual parsing if model didn't use native tool calls
            # (Simplified for now)
            return None

        results = []
        for tool_call in tool_calls:
            # Handle both Ollama and OpenAI tool call formats
            if "function" in tool_call:
                f = tool_call["function"]
                name = f["name"]
                args = f["arguments"]
                if isinstance(args, str):
                    args = json.loads(args)
            else:
                # Direct tool call format (some providers)
                name = tool_call.get("name")
                args = tool_call.get("args")

            if name in self.tools:
                tool_mod = self.tools[name]
                func = getattr(tool_mod, name if name != "bash" else "execute_bash")
                result = func(**args)
                results.append(result)
                self.transcript.append("assistant", content=f"Executed {name}", tool_calls=[tool_call], tool_results=[result])
            else:
                self.console.print(f"[bold red]Tool {name} not found.[/bold red]")
                results.append(f"Error: Tool {name} not found.")

        return results[0] if results else None
