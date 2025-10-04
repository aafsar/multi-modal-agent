import os
from dotenv import load_dotenv

load_dotenv()

# Deployment mode
DEPLOYMENT_MODE = os.getenv('DEPLOYMENT_MODE', 'local')  # 'local' or 'cloud'

# Voice engine selection
STT_ENGINE = os.getenv('STT_ENGINE', 'local')  # 'local' or 'api'
TTS_ENGINE = os.getenv('TTS_ENGINE', 'local')  # 'local' or 'api'

# Audio settings
SAMPLE_RATE = 16000
CHANNELS = 1
AUDIO_FORMAT = 'float32'
RECORD_MAX_SECONDS = 10

# Whisper settings (local)
WHISPER_MODEL = "base"  # For local STT
WHISPER_LANGUAGE = "en"

# TTS settings (local - pyttsx3)
TTS_RATE = 175
TTS_VOLUME = 0.9

# TTS settings (API - OpenAI)
OPENAI_TTS_VOICE = os.getenv('OPENAI_TTS_VOICE', 'alloy')
OPENAI_TTS_MODEL = "tts-1"  # or "tts-1-hd" for higher quality

# UI settings
ENABLE_COLORS = True
RECORDING_INDICATOR = "🔴 Recording..."
PROCESSING_INDICATOR = "⚙️  Processing..."
SPEAKING_INDICATOR = "🔊 Speaking..."

# Agent settings (from digital-twin-lite)
DATA_DIR = "./data"
KNOWLEDGE_DIR = "./knowledge"
SCHEDULE_PATH = "./data/schedule.csv"
PREFERENCES_PATH = "./knowledge/user_preference.txt"

# API settings
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Helper functions
def is_local_mode():
    return STT_ENGINE == 'local' and TTS_ENGINE == 'local'

def is_api_mode():
    return STT_ENGINE == 'api' and TTS_ENGINE == 'api'
