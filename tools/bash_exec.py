import asyncio
import subprocess
import os
import sys
from rich.console import Console
from rich.panel import Panel
from permissions import gate

def execute_bash(command: str, timeout: int = 30) -> dict:
    console = Console()

    destructive = gate.check_destructive_command(command)

    if not gate.ask_permission(f"Run this command?\n`{command}`", destructive=destructive):
        return {"stdout": "", "stderr": "Aborted by user.", "exit_code": 1}

    console.print(Panel(command, title="Executing Command", border_style="cyan"))

    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        stdout_output = []
        stderr_output = []

        # To achieve real-time streaming while still respecting timeout,
        # we can use poll and read.
        import time
        start_time = time.time()

        while True:
            # Check for timeout
            if time.time() - start_time > timeout:
                process.kill()
                stdout, stderr = process.communicate()
                stdout_output.append(stdout)
                stderr_output.append(stderr)
                console.print(f"[bold red]Command timed out after {timeout} seconds.[/bold red]")
                return {
                    "stdout": "".join(stdout_output),
                    "stderr": "".join(stderr_output) + f"\nError: Command timed out after {timeout}s.",
                    "exit_code": 124
                }

            # Read a line from stdout
            line = process.stdout.readline()
            if line:
                console.print(line.rstrip())
                stdout_output.append(line)

            # Check if process finished
            if line == '' and process.poll() is not None:
                break

        # Read remaining stderr
        stderr = process.stderr.read()
        if stderr:
            console.print(f"[bold red]{stderr.rstrip()}[/bold red]")
            stderr_output.append(stderr)

        return {
            "stdout": "".join(stdout_output),
            "stderr": "".join(stderr_output),
            "exit_code": process.returncode
        }

    except Exception as e:
        return {"stdout": "", "stderr": f"Error executing bash: {str(e)}", "exit_code": 1}

TOOL_SPEC = {
    "name": "bash",
    "description": "Execute a bash command with a 30s timeout and real-time output.",
    "parameters": {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The command to run."
            }
        },
        "required": ["command"]
    }
}
