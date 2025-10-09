# Voice-Enabled MIT AI Studio Course Assistant

A multi-modal AI agent that combines speech-to-text (STT) and text-to-speech (TTS) capabilities to provide voice and text interaction with an intelligent course assistant. Built for the MIT AI Studio Fall 2025 course.

## Features

- 🎤 **Voice Interaction:** Speak your questions using push-to-talk (Right CTRL)
- ⌨️ **Text Input:** Type complex queries for precision
- 🤖 **Multi-Agent System:** Intelligent routing to specialized agents:
  - Schedule Navigator (class schedules & assignments)
  - Topic Researcher (web research on course topics)
  - Study Coordinator (personalized study plans)
- 🧠 **Intent Classification:** Natural language understanding with GPT-4o-mini
- 🎯 **Context-Aware Responses:** Tailored answers based on your specific question

## Prerequisites

- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- OpenAI API key
- (Optional) Serper API key for web research

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/aafsar/multi-modal-agent.git
   cd multi-modal-agent
   ```

2. **Install dependencies using uv:**
   ```bash
   uv sync
   ```

3. **Set up environment variables:**
   Create a `.env` file in the project root:
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   SERPER_API_KEY=your_serper_api_key_here  # Optional, for web research
   ```

## Running the Agent

Start the voice assistant:

```bash
uv run main.py
```

## Usage

### Interaction Modes

When prompted, choose your input method:

- **Press `v`** → Voice mode (hold Right CTRL to speak)
- **Press `t`** → Text mode (type your question)
- **Press `e`** → Exit

### Example Queries

**Voice Questions:**
- "What is the topic of the next class?"
- "When is my next class?"
- "Tell me about multimodal AI"
- "Why should I care about AI agents?"

**Text Questions:**
- "Create my weekly plan for the next two weeks"
- "What are my Tech track assignments?"
- "Research the agentic web"

### Agent Capabilities

The assistant can help you with:

📚 **Next Class Information**
- Upcoming class dates, topics, and speakers
- Class preparation requirements

🔍 **Topic Research**
- Web research on course-related topics
- Speaker background and contributions
- Current trends and developments

📝 **Weekly Preparation Plan**
- Personalized study schedules
- Daily task breakdowns
- Homework reminders

📋 **Assignment Tracking**
- Track Tech/Analyst track assignments
- Due dates and status
- Upcoming deadlines

## Configuration

### Audio Settings (`config/settings.py`)

```python
# Recording settings
SAMPLE_RATE = 16000  # Hz
CHANNELS = 1  # Mono
RECORD_MAX_SECONDS = 30

# STT settings
STT_ENGINE = 'local'  # 'local' or 'api'
WHISPER_MODEL = 'base'  # base, small, medium, large

# TTS settings
TTS_ENGINE = 'local'  # 'local' or 'api'
TTS_RATE = 175  # Words per minute
TTS_VOLUME = 0.9  # 0.0 to 1.0
```

### Agent Configuration

Agents and tasks are configured in:
- `src/agent/config/agents.yaml` - Agent definitions
- `src/agent/config/tasks.yaml` - Task descriptions

## Architecture

```
Voice/Text Input
      ↓
Orchestrator (State Machine)
      ↓
Intent Classifier (GPT-4o-mini)
      ↓
┌─────────────────────────────────┐
│  Multi-Agent System (CrewAI)    │
│  • Schedule Navigator            │
│  • Topic Researcher              │
│  • Study Coordinator             │
└─────────────────────────────────┘
      ↓
Response (Text Panel / TTS)
```

## Technologies Used

- **STT:** OpenAI Whisper (local)
- **TTS:** pyttsx3 (offline)
- **Agent Framework:** CrewAI + OpenAI GPT-4/GPT-4o-mini
- **Audio:** sounddevice, pynput
- **UI:** Rich (Python terminal)

## Performance

| Mode | Average Response Time |
|------|----------------------|
| Voice | 25-35 seconds |
| Text | 10-12 seconds |

Breakdown:
- STT: ~1.8s
- Intent Classification: ~1.5s
- Agent Processing: ~8-10s
- TTS: ~5-20s (length-dependent)

## Troubleshooting

### macOS TTS Issues
If TTS stops working after the first interaction, the code includes an automatic fix (engine reinitialization). This is a known pyttsx3 limitation on macOS.

### Microphone Not Working
Ensure your terminal has microphone permissions:
- macOS: System Preferences → Security & Privacy → Microphone

### API Rate Limits
If you encounter rate limits:
- Use local Whisper model (default)
- Reduce frequency of topic research queries

## Project Structure

```
multi-modal-agent/
├── src/
│   ├── agent/           # CrewAI agents and configurations
│   ├── audio/           # Audio recording
│   ├── voice/           # STT and TTS
│   ├── ui/              # Terminal UI
│   └── orchestrator.py  # Main orchestration logic
├── config/              # Configuration files
├── data/                # Course schedule data
├── knowledge/           # User preferences
├── main.py             # Entry point
├── WRITEUP.md          # Implementation write-up (HW4 deliverable)
└── README.md           # This file
```


## License

MIT License - Built for educational purposes as part of MIT AI Studio Fall 2025.

## Author

Atahan Afsar

---
