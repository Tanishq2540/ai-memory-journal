import openai
import os
openai.api_key = os.getenv("OPENAI_API_KEY")


def is_input_safe(user_input):
    try:
        response = openai.Moderation.create(input=user_input)
        flagged = response["results"][0]["flagged"]
        return not flagged  # Returns True if safe
    except Exception as e:
        print(f"Moderation API error: {e}")
        return True 