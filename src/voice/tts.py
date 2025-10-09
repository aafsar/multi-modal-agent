import pyttsx3
import os
from config.settings import (
    TTS_ENGINE, TTS_RATE, TTS_VOLUME,
    OPENAI_TTS_VOICE, OPENAI_TTS_MODEL, OPENAI_API_KEY
)


class TextToSpeech:
    """Text-to-Speech using pyttsx3 (local) or OpenAI TTS API."""

    def __init__(self, engine=TTS_ENGINE, rate=TTS_RATE, volume=TTS_VOLUME):
        """
        Initialize TTS engine.

        Args:
            engine: 'local' for pyttsx3, 'api' for OpenAI TTS
            rate: Speech rate (words per minute) for local engine
            volume: Volume level (0.0 to 1.0) for local engine
        """
        self.engine_type = engine
        self.tts_engine = None
        self.rate = rate
        self.volume = volume

        if engine == 'local':
            try:
                self.tts_engine = pyttsx3.init()
                self.set_rate(rate)
                self.set_volume(volume)
            except Exception as e:
                raise
        elif engine == 'api':
            if not OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not set for API mode")
            from openai import OpenAI
            self.client = OpenAI(api_key=OPENAI_API_KEY)
        else:
            raise ValueError(f"Unknown TTS engine: {engine}")

    def speak(self, text: str):
        """
        Speak the given text.

        Args:
            text: Text to speak
        """
        if not text or len(text.strip()) == 0:
            return

        try:
            if self.engine_type == 'local':
                self._speak_local(text)
            elif self.engine_type == 'api':
                self._speak_api(text)
        except Exception as e:
            raise

    def _speak_local(self, text: str):
        """Speak using pyttsx3 local engine."""
        import platform

        # On macOS, pyttsx3 has issues with engine reuse after runAndWait()
        # Solution: Create a completely fresh engine instance each time
        if platform.system() == 'Darwin':  # macOS
            # Clean up old engine completely
            if self.tts_engine is not None:
                try:
                    del self.tts_engine
                except:
                    pass

            # Create brand new engine
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', self.rate)
            self.tts_engine.setProperty('volume', self.volume)

        # Speak the text
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    def _speak_api(self, text: str):
        """Speak using OpenAI TTS API."""
        # Generate speech
        response = self.client.audio.speech.create(
            model=OPENAI_TTS_MODEL,
            voice=OPENAI_TTS_VOICE,
            input=text
        )

        # Save to temporary file
        audio_file = "temp_speech.mp3"
        try:
            response.stream_to_file(audio_file)

            # Play audio using pygame
            self._play_audio_file(audio_file)

        finally:
            # Clean up temporary file
            if os.path.exists(audio_file):
                os.remove(audio_file)

    def _play_audio_file(self, filename: str):
        """Play audio file using pygame."""
        import pygame

        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()

        # Wait for playback to complete
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        pygame.mixer.quit()

    def set_rate(self, rate: int):
        """
        Set speech rate for local engine.

        Args:
            rate: Words per minute
        """
        if self.engine_type == 'local' and self.tts_engine:
            self.rate = rate
            self.tts_engine.setProperty('rate', rate)

    def set_volume(self, volume: float):
        """
        Set volume for local engine.

        Args:
            volume: Volume level (0.0 to 1.0)
        """
        if self.engine_type == 'local' and self.tts_engine:
            self.volume = volume
            self.tts_engine.setProperty('volume', volume)

    def list_voices(self) -> list:
        """
        List available voices (local engine only).

        Returns:
            List of voice names
        """
        if self.engine_type == 'local' and self.tts_engine:
            voices = self.tts_engine.getProperty('voices')
            return [voice.name for voice in voices]
        return []

    def cleanup(self):
        """Clean up TTS engine resources."""
        if self.engine_type == 'local' and self.tts_engine:
            try:
                self.tts_engine.stop()
            except:
                pass
