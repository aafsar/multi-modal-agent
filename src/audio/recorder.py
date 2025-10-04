import numpy as np
import sounddevice as sd
from pynput import keyboard
import threading
import time
from config.settings import SAMPLE_RATE, CHANNELS, RECORD_MAX_SECONDS


class AudioRecorder:
    """Records audio from microphone with push-to-talk functionality."""

    def __init__(self, sample_rate=SAMPLE_RATE, channels=CHANNELS):
        self.sample_rate = sample_rate
        self.channels = channels
        self.is_recording = False
        self.audio_data = []
        self.start_time = None

    def record_push_to_talk(self, quit_callback=None) -> np.ndarray:
        """
        Record audio while spacebar is held down.

        Args:
            quit_callback: Optional function to check if user wants to quit

        Returns:
            numpy array suitable for Whisper processing, or None if quit requested
        """
        self.audio_data = []
        self.is_recording = False
        self.quit_requested = False
        recording_complete = threading.Event()

        def on_press(key):
            """Start recording when Right Ctrl is pressed."""
            try:
                # Check for quit
                if hasattr(key, 'char') and key.char == 'q':
                    self.quit_requested = True
                    self.is_recording = False
                    recording_complete.set()
                    return False  # Stop listener

                # Start recording on Right Ctrl
                if key == keyboard.Key.ctrl_r and not self.is_recording:
                    self.is_recording = True
                    self.start_time = time.time()
                    self.audio_data = []
            except AttributeError:
                pass

        def on_release(key):
            """Stop recording when Right Ctrl is released."""
            if key == keyboard.Key.ctrl_r and self.is_recording:
                self.is_recording = False
                recording_complete.set()
                return False  # Stop listener

        # Start keyboard listener in non-blocking mode
        listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        listener.start()

        # Wait for spacebar press to start recording (or quit)
        while not self.is_recording and not self.quit_requested:
            time.sleep(0.01)

        # If quit requested, stop and return None
        if self.quit_requested:
            listener.stop()
            return None

        # Record audio while spacebar is held
        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype='float32',
            callback=self._audio_callback
        ):
            # Record until spacebar released or max duration reached
            while self.is_recording and not self.quit_requested:
                elapsed = time.time() - self.start_time
                if elapsed >= RECORD_MAX_SECONDS:
                    self.is_recording = False
                    recording_complete.set()
                    break
                time.sleep(0.01)

        listener.stop()

        # If quit requested during recording, return None
        if self.quit_requested:
            return None

        # Convert list of audio chunks to single numpy array
        if len(self.audio_data) > 0:
            audio_array = np.concatenate(self.audio_data, axis=0)
            # Convert to mono if stereo
            if len(audio_array.shape) > 1 and audio_array.shape[1] > 1:
                audio_array = np.mean(audio_array, axis=1)
            return audio_array.flatten().astype(np.float32)
        else:
            return np.array([], dtype=np.float32)

    def _audio_callback(self, indata, frames, time_info, status):
        """Callback function called by sounddevice for each audio block."""
        if status:
            print(f"Audio callback status: {status}")
        if self.is_recording:
            self.audio_data.append(indata.copy())

    def get_audio_level(self, data: np.ndarray) -> float:
        """
        Calculate RMS audio level for visualization.
        Returns value between 0.0 and 1.0.
        """
        if len(data) == 0:
            return 0.0
        return float(np.sqrt(np.mean(data**2)))

    def cleanup(self):
        """Clean up resources."""
        self.audio_data = []
        self.is_recording = False
