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
            "💡 [bold]How to interact:[/bold]",
            justify="center"
        )
        self.console.print(
            "   • Press [bold green]'v'[/bold green] then Enter → Voice mode (hold Right CTRL to speak)",
            justify="center"
        )
        self.console.print(
            "   • Press [bold cyan]'t'[/bold cyan] then Enter → Text mode (type and Enter)",
            justify="center"
        )
        self.console.print(
            "   • Press [bold red]'e'[/bold red] then Enter → Exit",
            justify="center"
        )
        self.console.print()

    def show_capabilities(self):
        """Display agent capabilities menu."""
        capabilities_text = """[bold]I can help you with:[/bold]

📚 [cyan]Next Class Information[/cyan]
   "When is my next class?" • "What's coming up?"

🔍 [cyan]Topic Research[/cyan]
   "Research multimodal AI" • "Tell me about AI agents"

📝 [cyan]Weekly Preparation Plan[/cyan]
   "Create my weekly plan" • "What should I prepare?"

📋 [cyan]Assignment Tracking[/cyan]
   "Show my assignments" • "Track Tech track homework"
"""
        capabilities_panel = Panel(
            capabilities_text.strip(),
            title="[bold yellow]I can help you with[/bold yellow]",
            box=ROUNDED,
            border_style="yellow",
            padding=(1, 2)
        )
        self.console.print(capabilities_panel, justify="center")

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

    def show_intent_detected(self, intent: str, params: dict = None):
        """
        Show detected intent to user for transparency.

        Args:
            intent: The detected intent
            params: Extracted parameters
        """
        intent_display = {
            'next_class': '📚 Next Class Information',
            'topic_research': '🔍 Topic Research',
            'weekly_plan': '📝 Weekly Preparation Plan',
            'assignments': '📋 Assignment Tracking',
            'help': '❓ Help/Capabilities'
        }

        display_name = intent_display.get(intent, intent)
        param_str = ""

        if params:
            if 'topic' in params:
                param_str = f" (Topic: {params['topic']})"
            elif 'track' in params:
                param_str = f" ({params['track']} Track)"

        self.console.print(f"\n🎯 [dim]Detected:[/dim] [cyan]{display_name}{param_str}[/cyan]")

    def ask_for_parameter(self, param_name: str, prompt_text: str = None) -> str:
        """
        Ask user for a missing parameter.

        Args:
            param_name: Name of the parameter needed
            prompt_text: Custom prompt text

        Returns:
            User's response
        """
        if prompt_text is None:
            if param_name == 'topic':
                prompt_text = "What topic would you like to research?"
            elif param_name == 'track':
                prompt_text = "Which track? (Tech/Analyst):"
            else:
                prompt_text = f"Please provide {param_name}:"

        self.console.print()
        self.console.print(f"❓ [bold yellow]{prompt_text}[/bold yellow]")
        response = input("   → ").strip()
        return response

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
            "[dim]─────────────────────────────────────────[/dim]",
            justify="center"
        )
        self.console.print()
        self.show_capabilities()

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
