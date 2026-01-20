from google import genai
from google.genai import types
import os

# 1. Initialize the new Client (reads API key from env or you can pass it directly)
# Make sure you set your env variable: export GEMINI_API_KEY="your_key"
client = genai.Client(api_key="AIzaSyBNVnoRHvXyIgLb90Odx66sbV91ngN9I8I")

# 2. The System Prompt (Your "Tv Critic" Persona)
system_instruction = """
You are a TV Show Recommendation expert. 
When a user asks for a recommendation, return exactly 3 shows in JSON format.
Include: 'title', 'year', 'streaming_service', and a 'reason' why it fits the user's mood.
"""

# 3. The User's Request
user_prompt = "I want a show like 'Severance' but with more comedy."

# 4. Generate Content with Gemini 3 Pro
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[user_prompt],
    config=types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.7,
        # This is the "Magic" of Gemini 3 - forcing it to reason before answering
        thinking_config=types.ThinkingConfig(
            include_thoughts=False # Set to True if you want to see HOW it found the show
        ), 
        response_mime_type="application/json" # Forces perfect JSON for your app
    )
)

# 5. Print the result
print(response.text)