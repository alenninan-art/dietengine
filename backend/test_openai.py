import os
from openai import OpenAI
from dotenv import load_dotenv

# Load from root .env manually if needed
load_dotenv(dotenv_path="../.env")

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if not api_key:
    print("Error: No API key found.")
    exit(1)

client_kwargs = {"api_key": api_key}
if base_url:
    client_kwargs["base_url"] = base_url

client = OpenAI(**client_kwargs)

try:
    print("Sending request to OpenAI...")
    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "Hello, are you working?"}],
        max_tokens=10,
        timeout=10
    )
    print("Success: OpenAI API is working!")
    print(f"Response: {completion.choices[0].message.content}")
except Exception as e:
    print(f"Error: OpenAI API call failed: {type(e).__name__} - {e}")
    import traceback
    traceback.print_exc()
