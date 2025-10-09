import numpy as np
import whisper
import time
import os
import soundfile as sf
from config.settings import WHISPER_MODEL, WHISPER_LANGUAGE, STT_ENGINE, OPENAI_API_KEY


class WhisperSTT:
    """Speech-to-Text using OpenAI Whisper (local or API)."""

    def __init__(self, engine=STT_ENGINE, model_name=WHISPER_MODEL):
        """
        Initialize Whisper STT.

        Args:
            engine: 'local' for local Whisper model, 'api' for OpenAI API
            model_name: Whisper model size (base, small, medium, large)
        """
        self.engine = engine
        self.model_name = model_name
        self.model = None
        self.last_processing_time = 0.0

        if engine == 'local':
            self.model = whisper.load_model(model_name)
        elif engine == 'api':
            if not OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not set for API mode")
            from openai import OpenAI
            self.client = OpenAI(api_key=OPENAI_API_KEY)
        else:
            raise ValueError(f"Unknown STT engine: {engine}")

    def transcribe(self, audio_data: np.ndarray) -> str:
        """
        Transcribe audio to text.

        Args:
            audio_data: NumPy array of audio samples (float32, mono, 16kHz)

        Returns:
            Transcribed text (trimmed and cleaned)
        """
        if len(audio_data) == 0:
            return ""

        start_time = time.time()

        try:
            if self.engine == 'local':
                text = self._transcribe_local(audio_data)
            elif self.engine == 'api':
                text = self._transcribe_api(audio_data)
            else:
                raise ValueError(f"Unknown STT engine: {self.engine}")

            self.last_processing_time = time.time() - start_time
            return text.strip()

        except Exception as e:
            self.last_processing_time = time.time() - start_time
            raise

    def _transcribe_local(self, audio_data: np.ndarray) -> str:
        """Transcribe using local Whisper model."""
        # Whisper expects float32 audio
        result = self.model.transcribe(
            audio_data,
            language=WHISPER_LANGUAGE,
            fp16=False  # Use FP32 for compatibility
        )
        return result["text"]

    def _transcribe_api(self, audio_data: np.ndarray) -> str:
        """Transcribe using OpenAI Whisper API."""
        # Save audio to temporary file (API requires file input)
        temp_file = "temp_audio.wav"

        try:
            # Write audio to WAV file
            sf.write(temp_file, audio_data, 16000)

            # Call OpenAI Whisper API
            with open(temp_file, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=WHISPER_LANGUAGE
                )

            return transcript.text

        finally:
            # Clean up temporary file
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def get_processing_time(self) -> float:
        """Get the processing time of the last transcription in seconds."""
        return self.last_processing_time
