#!/usr/bin/env python3
"""Quick test for audio recorder."""

import sys
import numpy as np
from src.audio.recorder import AudioRecorder


def main():
    print("=== Audio Recorder Test ===")
    print("Press and hold SPACEBAR to record (max 10 seconds)")
    print("Release SPACEBAR to stop recording\n")

    recorder = AudioRecorder()

    try:
        audio = recorder.record_push_to_talk()

        print(f"\n✅ Recording complete!")
        print(f"   Samples: {len(audio)}")
        print(f"   Duration: {len(audio) / recorder.sample_rate:.2f} seconds")
        print(f"   Audio level (RMS): {recorder.get_audio_level(audio):.4f}")

        if len(audio) > 0:
            # Optionally save to WAV for manual verification
            import soundfile as sf
            filename = "test_recording.wav"
            sf.write(filename, audio, recorder.sample_rate)
            print(f"   Saved to: {filename}")

    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        recorder.cleanup()


if __name__ == "__main__":
    main()
