import requests
import os
from dotenv import load_dotenv
import re

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Map moods to simple emojis
MOOD_EMOJI_MAP = {
    "happy": "😄",
    "sad": "😢",
    "angry": "😠",
    "anxious": "😰",
    "excited": "🤩",
    "calm": "😌",
    "tired": "😴",
    "stressed": "😫",
    "confused": "😕",
    "motivated": "💪",
    "grateful": "🙏",
    "lonely": "😔",
    "relaxed": "😌",
    "confident": "💪",
    "energized": "⚡",
    "neutral": "📝",
    "frustrated": "😣",
    "cheerful": "😀"
}


def generate_summary_and_reflection(entry, recent_moods=None):
    trend_text = ", ".join(recent_moods) if recent_moods else "No recent mood data."

    prompt = f"""
You are a supportive AI journal companion.

Analyze the following journal entry and provide:
1. A brief summary of the entry, speaking directly to the user as "you".
2. A motivational or thoughtful reflection based on the entry and the user's recent mood trend.
3. A one-word mood that best describes the current journal entry (e.g., happy, anxious, tired).

Recent mood trend: {trend_text}

INSTRUCTIONS:
- If a mood pattern exists (e.g., the user has felt "relaxed" for several days), explicitly acknowledge it in the reflection.
- Start that part of the reflection with this phrase exactly: "In recent days, ..."
- Avoid repeating the full entry text.
- Be warm, concise, and encouraging.
- End the response after the "Mood" line — do not include any additional content.

Respond exactly in this format:

Summary: ...
Reflection: ...
Mood: ...
Entry:
{entry}
"""


    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
    content = response.json()["choices"][0]["message"]["content"]

    # Parse the response
    try:
        summary = content.split("Summary:")[1].split("Reflection:")[0].strip()
        reflection = content.split("Reflection:")[1].split("Mood:")[0].strip()
        
        # Smarter mood extraction: split before "Entry:" to avoid accidental footnotes
        raw_mood_block = content.split("Mood:")[1].split("Entry:")[0].strip()
        mood = raw_mood_block.split("\n")[0].strip().lower()
    except IndexError:
        summary = "Summary not generated."
        reflection = "Reflection not generated."
        mood = "neutral"

    # Remove **bold** markdown if present
    def clean(text):
        return re.sub(r"\*\*(.*?)\*\*", r"\1", text).strip()

    summary = clean(summary)
    reflection = clean(reflection)
    mood = clean(mood)

    summary = clean(summary)
    reflection = clean(reflection)
    mood = clean(mood)

    emoji = MOOD_EMOJI_MAP.get(mood.strip().lower(), "📝")
    return summary, reflection, mood, emoji
