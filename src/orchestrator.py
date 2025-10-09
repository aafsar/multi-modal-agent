from enum import Enum
import time
from datetime import datetime

from src.audio.recorder import AudioRecorder
from src.voice.stt import WhisperSTT
from src.voice.tts import TextToSpeech
from src.agent.crew_agent import VoiceCourseAgent
from src.agent.intent_classifier import IntentClassifier
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
        self.intent_classifier = None

    def _init_components(self):
        """Initialize components on first use."""
        if self.recorder is None:
            self.recorder = AudioRecorder()

        if self.stt is None:
            self.stt = WhisperSTT()

        if self.tts is None:
            self.tts = TextToSpeech()

        if self.agent is None:
            self.agent = VoiceCourseAgent()

        if self.intent_classifier is None:
            self.intent_classifier = IntentClassifier()


    def run(self):
        """Main conversation loop."""
        self.ui.show_welcome()

        # Initialize components
        self._init_components()

        try:
            while not self.should_exit:
                self.state = State.IDLE
                self.ui.show_prompt()

                # Wait for user input (voice or text)
                try:
                    mode, data = self.wait_for_user_input()

                    if mode == 'exit':
                        self.should_exit = True
                        break
                    elif mode == 'voice':
                        # data is audio numpy array
                        self.handle_voice_turn(audio_data=data)
                    elif mode == 'text':
                        # data is text string
                        self.handle_text_turn(data)

                except KeyboardInterrupt:
                    break
                except Exception as e:
                    self.handle_error(e)

        finally:
            self.cleanup()

    def wait_for_user_input(self) -> tuple:
        """
        Wait for user input - simple v/t/e mode selection.

        Returns:
            tuple: (mode, data) where mode is 'voice', 'text', or 'exit'
                   For voice: data is audio numpy array
                   For text: data is the text string
        """
        self.ui.console.print()
        choice = input("Press (v) for voice, (t) for text, or (e) to exit, then ENTER: ").strip().lower()

        if choice == 'v':
            # Voice mode
            self.ui.console.print("\n🎤 [green]Press and hold Right CTRL to speak...[/green]")
            audio = self.recorder.record_push_to_talk()
            return ('voice', audio)

        elif choice == 't':
            # Text mode
            text = input("\nType your question and press ENTER: ").strip()
            if text == '/exit':
                return ('exit', None)
            return ('text', text)

        elif choice == 'e' or choice == '/exit':
            return ('exit', None)

        else:
            # Invalid choice - reprompt
            self.ui.console.print("❌ [red]Invalid choice. Please press 'v', 't', or 'e'.[/red]")
            return self.wait_for_user_input()

    def classify_and_execute_intent(self, user_text: str) -> tuple[str, float]:
        """
        Classify user intent and execute the appropriate agent task.

        Args:
            user_text: The user's question or request

        Returns:
            Tuple of (response_text, agent_time)
        """
        current_date = datetime.now().strftime("%m/%d/%Y")

        # Classify intent
        classification = self.intent_classifier.classify(user_text, default_track='Tech')
        intent = classification['intent']
        params = classification['params']

        # Handle help intent
        if intent == 'help':
            # Check if user explicitly asked for help
            if user_text.lower() in ['help', '/help', 'menu']:
                self.ui.console.print("\n💡 [cyan]Here's what I can help you with:[/cyan]")
            else:
                self.ui.console.print("\n💡 [yellow]I can't help you with that currently. See below for what I can help you with:[/yellow]")
            return "", 0.0

        # Check for missing parameters
        if classification.get('needs_clarification'):
            # Ask for missing information
            clarification = classification.get('clarification_question', '')
            if clarification:
                self.ui.console.print(f"\n❓ [yellow]{clarification}[/yellow]")
                return "", 0.0

            # Prompt for specific parameter
            if intent == 'topic_research' and 'topic' not in params:
                topic = self.ui.ask_for_parameter('topic')
                if not topic:
                    return "", 0.0
                params['topic'] = topic

        # Execute intent
        agent_start = time.time()

        try:
            if intent == 'next_class':
                response_text = self.agent.get_next_class_info(user_text, current_date)

            elif intent == 'topic_research':
                topic = params.get('topic', 'AI Agents')
                response_text = self.agent.research_topic(user_text, topic, current_date)

            elif intent == 'weekly_plan':
                response_text = self.agent.get_weekly_plan(user_text, current_date)

            elif intent == 'assignments':
                track = params.get('track', 'Tech')
                response_text = self.agent.track_assignments(user_text, track, current_date)

            else:
                # Fallback to next class info
                response_text = self.agent.get_next_class_info(user_text, current_date)

            agent_time = time.time() - agent_start
            return response_text, agent_time

        except Exception as e:
            self.ui.show_error(f"Error executing task: {str(e)}")
            return "", 0.0

    def handle_text_turn(self, user_text: str):
        """Handle one complete text-based interaction turn."""
        turn_start = time.time()

        try:
            if not user_text or len(user_text.strip()) == 0:
                self.ui.show_error("Empty input. Please try again.")
                return

            # No need to show transcription for text (user already sees what they typed)

            # THINKING: Process with AI agent
            self.state = State.THINKING
            self.ui.show_thinking()

            # Classify intent and execute
            response_text, agent_time = self.classify_and_execute_intent(user_text)

            # Display response (text only, no TTS)
            if response_text:
                self.ui.show_response(response_text)

            # Update metrics (no STT or TTS for text mode)
            total_time = time.time() - turn_start
            self._update_metrics(0, agent_time, 0, total_time)

        except Exception as e:
            self.state = State.ERROR
            raise

    def handle_voice_turn(self, audio_data=None):
        """
        Handle one complete voice interaction turn.

        Args:
            audio_data: Optional pre-recorded audio array. If None, will record.
        """
        turn_start = time.time()

        try:
            # RECORDING: Capture audio (if not provided)
            if audio_data is None:
                self.state = State.RECORDING
                self.ui.show_recording()
                audio = self.recorder.record_push_to_talk()
            else:
                # Audio already recorded in wait_for_user_input()
                audio = audio_data

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

            # Classify intent and execute
            response_text, agent_time = self.classify_and_execute_intent(transcribed_text)

            # Display response
            if response_text:
                self.ui.show_response(response_text)

                # SPEAKING: Convert response to speech
                self.state = State.SPEAKING
                self.ui.show_speaking()

                tts_start = time.time()
                self.tts.speak(response_text)
                tts_time = time.time() - tts_start
            else:
                # No response (e.g., help command)
                tts_time = 0

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

        # Cleanup components
        if self.recorder:
            self.recorder.cleanup()
        if self.tts:
            self.tts.cleanup()
        if self.agent:
            self.agent.cleanup()
