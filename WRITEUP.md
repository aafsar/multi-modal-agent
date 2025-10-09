# Voice-Enabled Multi-Modal Agent: Implementation Write-up

**Course:** MIT AI Studio Fall 2025
**Assignment:** HW4 - Build a Multimodal Agent
**Student:** Atahan Afsar

---

## 1. Implementation Overview

This project extends the MIT AI Studio Course Assistant (from HW1-HW3) with speech capabilities, enabling voice-based interaction alongside traditional text input. The system supports bidirectional voice communication through Speech-to-Text (STT) and Text-to-Speech (TTS) integration.

### Architecture

The voice-enabled agent follows a modular architecture with the following key components:

```
┌─────────────────────────────────────────────────────────┐
│                   User Interface Layer                   │
│              (Rich Terminal UI + Audio I/O)              │
└─────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────┐
│                  Orchestration Layer                     │
│   (State Machine: IDLE → RECORDING → PROCESSING →       │
│                THINKING → SPEAKING)                      │
└─────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┴──────────────────┐
        │                                      │
┌───────▼────────┐                    ┌───────▼────────┐
│  Voice Pipeline│                    │  Text Pipeline │
│  STT → Agent   │                    │  Agent → TTS   │
│    → TTS       │                    │                │
└────────────────┘                    └────────────────┘
                           │
┌─────────────────────────────────────────────────────────┐
│              Multi-Agent AI System (CrewAI)             │
│  • Schedule Navigator  • Topic Researcher               │
│  • Study Coordinator   • Intent Classifier              │
└─────────────────────────────────────────────────────────┘
```

## 2. Technology Stack

### Speech-to-Text (STT)
- **Library:** OpenAI Whisper (local model)
- **Model:** `base` (74M parameters)
- **Implementation:**
  ```python
  import whisper

  model = whisper.load_model("base")
  result = model.transcribe(audio_data, language="en", fp16=False)
  transcribed_text = result["text"]
  ```
- **Audio Format:** Float32, mono, 16kHz sample rate
- **Processing Time:** ~1.8 seconds per transcription

### Text-to-Speech (TTS)
- **Library:** pyttsx3 (offline TTS engine)
- **Platform:** Uses native engines (NSSpeechSynthesizer on macOS)
- **Configuration:**
  - Speech Rate: 175 words/minute
  - Volume: 0.9 (90%)
- **macOS-specific workaround:** Engine reinitialization per call to prevent silent playback bug
  ```python
  if platform.system() == 'Darwin':
      self.tts_engine = pyttsx3.init()  # Fresh instance each time
      self.tts_engine.setProperty('rate', self.rate)
      self.tts_engine.setProperty('volume', self.volume)
  ```

### Audio Recording
- **Library:** sounddevice + pynput
- **Mode:** Push-to-talk (Right CTRL key)
- **Implementation:**
  ```python
  with sd.InputStream(samplerate=16000, channels=1, dtype='float32'):
      # Record while Right CTRL is held
      while self.is_recording:
          # Audio captured via callback
  ```

### AI Agent Framework
- **Framework:** CrewAI with OpenAI GPT-4
- **Intent Classification:** GPT-4o-mini for fast, cost-effective routing
- **Agents:**
  - **Schedule Navigator:** Parses course schedule, tracks assignments
  - **Topic Researcher:** Web research using SerperDevTool + WebsiteSearchTool
  - **Study Coordinator:** Creates personalized study plans
- **Intent Classifier:** Routes natural language queries to appropriate agent

### User Interface
- **Library:** Rich (Python terminal formatting)
- **Features:** Colored output, formatted panels, status indicators

## 3. Key Implementation Decisions

### 1. Hybrid Input System
Users can choose between voice and text input at each interaction:
- Press `v` → Voice mode (hold Right CTRL to speak)
- Press `t` → Text mode (type and press Enter)
- Press `e` → Exit

**Rationale:** Provides flexibility for different contexts (noisy environments, complex queries, accessibility needs)

### 2. Intent-Based Task Routing
Instead of running all agent tasks sequentially, the system:
1. Classifies user intent using GPT-4o-mini (~1-2 second overhead)
2. Routes to specific agent task (next_class, topic_research, weekly_plan, assignments)
3. Passes original question to agent for tailored responses

**Benefit:** User can ask "What's the date of my next class?" and get just the date, not a full briefing.

### 3. Concise Responses for Voice
Research tasks default to 2-3 sentence answers unless user explicitly requests "detailed" or "comprehensive" information.

**Rationale:** Voice interactions favor brevity; long responses are tedious to listen to.

## 4. Example Run: Three-Part Interaction

### Voice Question 1: "What is the topic of the next class?"

**Flow:**
1. User presses `v` → Voice mode activated
2. User holds Right CTRL → "🔴 Recording... Speak now..."
3. STT transcription: "What is the topic of the next class?"
4. Intent classification: `next_class` (with parameter extraction)
5. Schedule Navigator agent executes with user question context
6. Response synthesized via TTS

**Expected Output (Voice):**

---

### Voice Question 2: "Why should I care about Multimodal AI?"

**Flow:**
1. User presses `v` → Voice mode
2. User speaks question
3. Intent classification: `topic_research` (topic extracted: "Multimodal AI")
4. Topic Researcher agent uses SerperDevTool for web research
5. Agent generates concise 2-3 sentence response
6. TTS speaks the answer

**Expected Output (Voice):**


**Insights:**
- Web research adds ~3-5s latency
- Agent produces naturally witty/engaging tone when prompted correctly
- Concise task configuration prevents overly long responses

---

### Text Question: "Create my weekly plan for the next two weeks"

**Flow:**
1. User presses `t` → Text mode
2. User types: "Create my weekly plan for the next two weeks"
3. Intent classification: `weekly_plan`
4. Study Coordinator agent:
   - Reads schedule.csv
   - Reads user_preference.txt (learning style: visual learner, prefers hands-on)
   - Generates personalized 2-week plan
5. Response displayed in terminal (no TTS for text mode)

**Expected Output (Text Panel):**


**Insights:**
- Text mode skips STT and TTS, reducing latency to ~10 seconds
- Study Coordinator successfully integrates user preferences
- Weekly plan is actionable and personalized

---

## 5. Technical Challenges & Solutions

### Challenge 1: Push-to-Talk Workflow
**Problem:** Initial implementation using blocking `input()` required pressing Enter after holding Right CTRL, breaking the natural voice workflow.

**Solution:** Explicit mode selection (v/t/e) before interaction, with Right CTRL triggering recording only after voice mode is selected. A UI where user explicitly presses "voice" button would be the best solution (for future work).

### Challenge 2: TTS Silent on Subsequent Calls (macOS)
**Problem:** pyttsx3 worked once, then failed silently on subsequent interactions.

**Solution:** Reinitialize engine before each speech on macOS:
```python
if platform.system() == 'Darwin':
    del self.tts_engine
    self.tts_engine = pyttsx3.init()
```

### Challenge 3: Agent Task Caching
**Problem:** CrewAI's `@crew` decorator cached tasks, causing "list index out of range" errors when trying to run individual tasks.

**Solution:** Create fresh `Crew()` instances for each task:
```python
crew = Crew(
    agents=[self.topic_researcher()],
    tasks=[self.topic_primer()],
    process=Process.sequential,
    verbose=False,
    memory=False,
    output_log_file=False
)
```


## 6. Observations & Insights

1. **Latency Trade-offs:** Voice interaction adds ~25-30s overhead (STT + TTS). Acceptable for conversational use but not real-time applications.

2. **Natural Language Understanding:** Intent classification using GPT-4o-mini is remarkably accurate, correctly routing questions like "Why should I care about X?" to topic research.

3. **User Experience:** Hybrid input (voice + text) significantly improves usability. Complex queries benefit from text input for precision.

4. **Agent Response Quality:** Passing the original user question to agents (instead of generic task descriptions) dramatically improved response relevance. The agent now provides concise answers to specific questions.

5. **Platform Dependencies:** macOS-specific bugs (TTS engine reuse) highlight the importance of platform testing in voice applications.

6. **Cost Efficiency:** Using local Whisper (base) model saves API costs compared to cloud STT. pyttsx3 provides free, offline TTS.

## 7. Future Enhancements

- **Streaming TTS:** Reduce perceived latency by starting audio playback before full response is generated
- **Voice Activity Detection:** Replace push-to-talk with automatic speech detection
- **Multi-turn Conversations:** Add memory/context for follow-up questions
- **Custom Wake Word:** Enable hands-free activation ("Hey Assistant...")
- **Emotion Detection:** Analyze voice tone to personalize responses

---

## Repository & Demo

**GitHub Repository:** https://github.com/aafsar/multi-modal-agent

---

**Technologies Used:**
- OpenAI Whisper (STT)
- pyttsx3 (TTS)
- CrewAI + OpenAI GPT-4/GPT-4o-mini (Agent Framework)
- sounddevice + pynput (Audio Recording)
- Rich (Terminal UI)
- Python 3.11+
