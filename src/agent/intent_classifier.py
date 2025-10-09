"""Intent classification for natural language queries to agent tasks."""

import os
import json
from typing import Dict, Any
from openai import OpenAI


class IntentClassifier:
    """Classifies user intent and extracts parameters for agent routing."""

    INTENTS = {
        'next_class': 'User wants information about the next upcoming class',
        'topic_research': 'User wants to research a specific topic',
        'weekly_plan': 'User wants a weekly preparation plan',
        'assignments': 'User wants to track assignments',
        'help': 'User wants to see available capabilities/menu'
    }

    def __init__(self):
        """Initialize the intent classifier with OpenAI client."""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        self.client = OpenAI(api_key=api_key)

    def classify(self, user_query: str, default_track: str = 'Tech') -> Dict[str, Any]:
        """
        Classify user intent and extract parameters.

        Args:
            user_query: The user's question or request
            default_track: Default track to use if not specified (Tech/Analyst)

        Returns:
            Dictionary with:
                - intent: str (next_class|topic_research|weekly_plan|assignments|help)
                - params: dict (extracted parameters like topic, track)
                - confidence: float (0.0-1.0)
                - needs_clarification: bool (True if missing required params)
                - clarification_question: str (question to ask user)
        """
        system_prompt = f"""You are an intent classifier for an MIT AI Studio course assistant.

Available intents:
- next_class: User wants info about next upcoming class
- topic_research: User wants to research a topic (requires: topic name)
- weekly_plan: User wants a weekly preparation plan
- assignments: User wants to track assignments (optional: Tech/Analyst track)
- help: User wants to see what the assistant can do

Analyze the user query and return JSON:
{{
    "intent": "intent_name",
    "params": {{"topic": "...", "track": "Tech|Analyst"}},
    "confidence": 0.95,
    "needs_clarification": false,
    "clarification_question": ""
}}

Rules:
1. If topic_research but no topic mentioned: needs_clarification=true, ask for topic
2. For assignments: default to "{default_track}" track if not specified
3. Confidence should reflect how certain you are about the intent
4. Be liberal with help intent - if user asks "what can you do", it's help
"""

        user_prompt = f"User query: \"{user_query}\""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,  # Low temperature for consistent classification
                max_tokens=200,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)

            # Validate intent
            if result.get('intent') not in self.INTENTS:
                # Default to help if uncertain
                result['intent'] = 'help'
                result['confidence'] = 0.5

            # Ensure all required fields exist
            result.setdefault('params', {})
            result.setdefault('confidence', 0.8)
            result.setdefault('needs_clarification', False)
            result.setdefault('clarification_question', '')

            return result

        except Exception as e:
            # Fallback on error
            print(f"Intent classification error: {e}")
            return {
                'intent': 'help',
                'params': {},
                'confidence': 0.0,
                'needs_clarification': False,
                'clarification_question': ''
            }

    def get_capabilities_description(self) -> str:
        """
        Get a human-readable description of agent capabilities.

        Returns:
            String describing what the agent can do
        """
        return """I can help you with:

📚 **Next Class Information** - "When is my next class?" or "What's coming up?"
🔍 **Topic Research** - "Research multimodal AI" or "Tell me about AI agents"
📝 **Weekly Preparation Plan** - "Create my weekly plan" or "What should I prepare?"
📋 **Assignment Tracking** - "Show my assignments" or "Track Tech track homework"

Just ask me naturally in voice or text!"""
