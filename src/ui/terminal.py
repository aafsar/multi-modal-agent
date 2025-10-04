from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.box import ROUNDED
from config.settings import (
    ENABLE_COLORS,
    RECORDING_INDICATOR,
    PROCESSING_INDICATOR,
    SPEAKING_INDICATOR
)


class TerminalUI:
    """Rich terminal interface for voice assistant."""

    def __init__(self, enable_colors=ENABLE_COLORS):
        self.console = Console()
        self.enable_colors = enable_colors

    def show_welcome(self):
        """Display welcome message."""
        self.console.clear()

        title = Text("🎓 Voice-Enabled MIT AI Studio Assistant", style="bold cyan")
        welcome_panel = Panel(
            title,
            box=ROUNDED,
            border_style="cyan",
            padding=(1, 2)
        )

        self.console.print(welcome_panel)
        self.console.print()
        self.console.print(
            "💡 [bold]Two ways to interact:[/bold]",
            justify="center"
        )
        self.console.print(
            "   🎤 [bold green]Voice:[/bold green] Press and hold Right CTRL",
            justify="center"
        )
        self.console.print(
            "   ⌨️  [bold cyan]Text:[/bold cyan] Type your question and press Enter",
            justify="center"
        )
        self.console.print(
            "   [dim]Type '/exit' to quit[/dim]",
            justify="center"
        )
        self.console.print()

    def show_recording(self):
        """Show recording indicator."""
        self.console.print(f"\n{RECORDING_INDICATOR} [bold red]Speak now...[/bold red]")

    def show_processing(self):
        """Show processing indicator."""
        self.console.print(f"{PROCESSING_INDICATOR} [yellow]Transcribing audio...[/yellow]")

    def show_transcription(self, text: str):
        """
        Display transcribed text.

        Args:
            text: The transcribed text from speech
        """
        self.console.print(f"\n📝 [bold]You said:[/bold] [italic]\"{text}\"[/italic]")

    def show_thinking(self):
        """Show agent thinking indicator."""
        self.console.print(f"\n{PROCESSING_INDICATOR} [cyan]Processing with AI agent...[/cyan]")

    def show_response(self, text: str):
        """
        Display agent response in a formatted panel.

        Args:
            text: The agent's response text
        """
        self.console.print()

        response_panel = Panel(
            text,
            title="[bold cyan]Agent Response[/bold cyan]",
            box=ROUNDED,
            border_style="green",
            padding=(1, 2)
        )

        self.console.print(response_panel)

    def show_speaking(self):
        """Show TTS speaking indicator."""
        self.console.print(f"\n{SPEAKING_INDICATOR} [magenta]Speaking response...[/magenta]")

    def show_error(self, error: str):
        """
        Display error message.

        Args:
            error: Error message to display
        """
        error_panel = Panel(
            f"[bold red]Error:[/bold red] {error}",
            box=ROUNDED,
            border_style="red",
            padding=(1, 2)
        )

        self.console.print()
        self.console.print(error_panel)

    def show_goodbye(self):
        """Display goodbye message."""
        self.console.print()
        self.console.print(
            "[bold cyan]👋 Thank you for using the Voice Assistant. Goodbye![/bold cyan]",
            justify="center"
        )
        self.console.print()

    def show_prompt(self):
        """Show prompt for next action."""
        self.console.print()
        self.console.print(
            "[dim]💬 Voice: Right CTRL  •  ⌨️  Text: Type below  •  Exit: /exit[/dim]",
            justify="center"
        )
        self.console.print()

    def show_metrics(self, metrics: dict):
        """
        Display performance metrics.

        Args:
            metrics: Dictionary with timing and performance data
        """
        metrics_text = f"""
[bold]Performance Metrics:[/bold]
  • Total interactions: {metrics.get('total_turns', 0)}
  • Average response time: {metrics.get('avg_total_time', 0):.2f}s
  • STT time: {metrics.get('avg_stt_time', 0):.2f}s
  • Agent time: {metrics.get('avg_agent_time', 0):.2f}s
  • TTS time: {metrics.get('avg_tts_time', 0):.2f}s
"""

        self.console.print(Panel(
            metrics_text.strip(),
            title="[bold yellow]📊 Stats[/bold yellow]",
            box=ROUNDED,
            border_style="yellow"
        ))
