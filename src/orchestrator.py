from enum import Enum
import time
from datetime import datetime

from src.audio.recorder import AudioRecorder
from src.voice.stt import WhisperSTT
from src.voice.tts import TextToSpeech
from src.agent.crew_agent import VoiceCourseAgent
from src.ui.terminal import TerminalUI


class State(Enum):
    """States for the voice assistant state machine."""
    IDLE = "idle"
    RECORDING = "recording"
    PROCESSING = "processing"
    THINKING = "thinking"
    SPEAKING = "speaking"
    ERROR = "error"
    EXIT = "exit"


class VoiceOrchestrator:
    """Main orchestrator for voice-enabled course assistant."""

    def __init__(self):
        """Initialize all components."""
        self.ui = TerminalUI()
        self.state = State.IDLE
        self.should_exit = False

        # Performance metrics
        self.metrics = {
            'total_turns': 0,
            'avg_stt_time': 0.0,
            'avg_agent_time': 0.0,
            'avg_tts_time': 0.0,
            'avg_total_time': 0.0,
            'errors': 0
        }

        # Initialize components lazily (on first use)
        self.recorder = None
        self.stt = None
        self.tts = None
        self.agent = None

    def _init_components(self):
        """Initialize components on first use."""
        if self.recorder is None:
            self.ui.console.print("[dim]Initializing audio recorder...[/dim]")
            self.recorder = AudioRecorder()

        if self.stt is None:
            self.ui.console.print("[dim]Loading speech-to-text engine...[/dim]")
            self.stt = WhisperSTT()

        if self.tts is None:
            self.ui.console.print("[dim]Initializing text-to-speech engine...[/dim]")
            self.tts = TextToSpeech()

        if self.agent is None:
            self.ui.console.print("[dim]Loading AI agent...[/dim]")
            self.agent = VoiceCourseAgent()

        self.ui.console.print("[bold green] All systems ready![/bold green]\n")

    def run(self):
        """Main conversation loop."""
        self.ui.show_welcome()

        # Initialize components
        self._init_components()

        try:
            while not self.should_exit:
                self.state = State.IDLE
                self.ui.show_prompt()

                # Handle one voice interaction
                try:
                    self.handle_voice_turn()
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    self.handle_error(e)

        finally:
            self.cleanup()

    def handle_voice_turn(self):
        """Handle one complete voice interaction turn."""
        turn_start = time.time()

        try:
            # RECORDING: Capture audio
            self.state = State.RECORDING
            self.ui.show_recording()
            audio = self.recorder.record_push_to_talk()

            # Check if user pressed 'q' to quit
            if audio is None:
                self.should_exit = True
                return

            if len(audio) == 0:
                self.ui.show_error("No audio recorded. Please try again.")
                return

            # PROCESSING: Transcribe speech to text
            self.state = State.PROCESSING
            self.ui.show_processing()

            stt_start = time.time()
            transcribed_text = self.stt.transcribe(audio)
            stt_time = time.time() - stt_start

            if not transcribed_text or len(transcribed_text.strip()) == 0:
                self.ui.show_error("Could not understand speech. Please try again.")
                return

            self.ui.show_transcription(transcribed_text)

            # THINKING: Process with AI agent
            self.state = State.THINKING
            self.ui.show_thinking()

            agent_start = time.time()
            current_date = datetime.now().strftime("%m/%d/%Y")
            response_text = self.agent.get_next_class_info(current_date)
            agent_time = time.time() - agent_start

            # Display response
            self.ui.show_response(response_text)

            # SPEAKING: Convert response to speech
            self.state = State.SPEAKING
            self.ui.show_speaking()

            tts_start = time.time()
            self.tts.speak(response_text)
            tts_time = time.time() - tts_start

            # Update metrics
            total_time = time.time() - turn_start
            self._update_metrics(stt_time, agent_time, tts_time, total_time)

        except Exception as e:
            self.state = State.ERROR
            raise

    def handle_error(self, error: Exception):
        """
        Handle errors gracefully.

        Args:
            error: The exception that occurred
        """
        self.metrics['errors'] += 1
        self.ui.show_error(str(error))
        self.state = State.IDLE

    def _update_metrics(self, stt_time, agent_time, tts_time, total_time):
        """Update performance metrics."""
        n = self.metrics['total_turns']
        self.metrics['total_turns'] = n + 1

        # Running average
        self.metrics['avg_stt_time'] = (
            (self.metrics['avg_stt_time'] * n + stt_time) / (n + 1)
        )
        self.metrics['avg_agent_time'] = (
            (self.metrics['avg_agent_time'] * n + agent_time) / (n + 1)
        )
        self.metrics['avg_tts_time'] = (
            (self.metrics['avg_tts_time'] * n + tts_time) / (n + 1)
        )
        self.metrics['avg_total_time'] = (
            (self.metrics['avg_total_time'] * n + total_time) / (n + 1)
        )

    def cleanup(self):
        """Clean up all resources."""
        self.ui.show_goodbye()

        # Show final metrics if there were any turns
        if self.metrics['total_turns'] > 0:
            self.ui.show_metrics(self.metrics)

        # Cleanup components
        if self.recorder:
            self.recorder.cleanup()
        if self.tts:
            self.tts.cleanup()
        if self.agent:
            self.agent.cleanup()
