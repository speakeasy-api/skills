"""Execution observers for real-time agent event streaming."""

import json
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from .evaluator import AgentEvent


class RichConsoleObserver:
    """Observer that renders agent events to a Rich console in real-time."""

    def __init__(self, console: Console | None = None):
        self.console = console or Console()
        self._start_time: datetime | None = None

    def _format_timestamp(self, timestamp: datetime) -> str:
        """Format timestamp as HH:MM:SS."""
        return timestamp.strftime("%H:%M:%S")

    def _format_elapsed(self, timestamp: datetime) -> str:
        """Format elapsed time since start."""
        if self._start_time is None:
            self._start_time = timestamp
            return "0.0s"
        elapsed = (timestamp - self._start_time).total_seconds()
        return f"{elapsed:.1f}s"

    async def on_event(self, event: AgentEvent) -> None:
        """Handle an agent event by rendering it to the console."""
        ts = self._format_timestamp(event.timestamp)
        elapsed = self._format_elapsed(event.timestamp)

        if event.type == "turn":
            turn = event.content.get("turn", 0)
            max_turns = event.content.get("max_turns", 0)
            self.console.print()
            self.console.print(
                f"[dim]{ts}[/] [bold blue]Turn {turn}/{max_turns}[/]",
                highlight=False,
            )

        elif event.type == "thinking":
            thinking_text = event.content
            if len(thinking_text) > 500:
                thinking_text = thinking_text[:500] + "..."
            self.console.print(
                f"[dim]{ts}[/] [cyan]Thinking...[/]",
                highlight=False,
            )
            self.console.print(
                Panel(
                    thinking_text,
                    title="[dim]Thinking[/]",
                    style="dim cyan",
                    border_style="dim",
                ),
            )

        elif event.type == "text":
            text = event.content
            if text.strip():
                # Truncate very long text output
                if len(text) > 300:
                    text = text[:300] + "..."
                self.console.print(
                    f"[dim]{ts}[/] [green]Agent:[/] {text}",
                    highlight=False,
                )

        elif event.type == "tool_use":
            tool_name = event.content.get("name", "unknown")
            tool_input = event.content.get("input", {})

            # Format tool input as JSON, truncated
            try:
                input_str = json.dumps(tool_input, indent=2)
                if len(input_str) > 400:
                    input_str = input_str[:400] + "\n... (truncated)"
            except (TypeError, ValueError):
                input_str = str(tool_input)[:400]

            # Color-code by tool type
            tool_colors = {
                "Skill": "magenta",
                "Bash": "yellow",
                "Read": "blue",
                "Write": "green",
                "Glob": "cyan",
                "Grep": "cyan",
            }
            color = tool_colors.get(tool_name, "white")

            self.console.print(
                f"[dim]{ts}[/] [{color}]Tool: {tool_name}[/]",
                highlight=False,
            )
            self.console.print(
                Panel(
                    Syntax(input_str, "json", theme="monokai", word_wrap=True),
                    border_style=color,
                ),
            )

        elif event.type == "input_request":
            questions = event.content.get("questions", [])
            auto_answers = event.content.get("auto_answers", {})

            self.console.print()
            self.console.print(
                f"[dim]{ts}[/] [bold yellow]Clarifying Question (AskUserQuestion)[/]",
                highlight=False,
            )

            for q in questions:
                question_text = q.get("question", "")
                header = q.get("header", "")
                options = q.get("options", [])
                multi_select = q.get("multiSelect", False)
                auto_answer = auto_answers.get(question_text, "")

                # Build question display
                question_lines = []
                if header:
                    question_lines.append(f"[bold]{header}[/]: {question_text}")
                else:
                    question_lines.append(f"[bold]{question_text}[/]")

                if multi_select:
                    question_lines.append("[dim](multi-select)[/]")

                question_lines.append("")
                for i, opt in enumerate(options):
                    label = opt.get("label", "")
                    desc = opt.get("description", "")
                    # Mark auto-selected option
                    if label == auto_answer:
                        question_lines.append(f"  [green]→ {i + 1}. {label}[/] - {desc} [green](auto-selected)[/]")
                    else:
                        question_lines.append(f"  [dim]{i + 1}. {label} - {desc}[/]")

                self.console.print(
                    Panel(
                        "\n".join(question_lines),
                        title="[yellow]Question[/]",
                        border_style="yellow",
                    ),
                )

        elif event.type == "result":
            cost = event.content.get("cost_usd") or 0
            turns = event.content.get("turns_used", 0)
            self.console.print()
            self.console.print(
                f"[dim]{ts}[/] [bold]Complete[/] - "
                f"Turns: {turns}, "
                f"Cost: ${cost:.4f}, "
                f"Elapsed: {elapsed}",
                highlight=False,
            )
