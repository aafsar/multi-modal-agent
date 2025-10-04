#!/usr/bin/env python3
"""
Voice-Enabled MIT AI Studio Course Assistant

Main entry point for the voice-enabled course assistant.
Extends digital-twin-lite CrewAI agent with speech capabilities (STT + TTS).

Usage:
    python main.py
"""

import sys
from src.orchestrator import VoiceOrchestrator
from src.ui.terminal import TerminalUI


def main():
    """Main entry point."""
    # Create UI for error messages
    ui = TerminalUI()

    # Create and run orchestrator
    orchestrator = VoiceOrchestrator()

    try:
        orchestrator.run()
    except KeyboardInterrupt:
        ui.show_goodbye()
        sys.exit(0)
    except Exception as e:
        ui.show_error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
