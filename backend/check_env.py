import os
from dotenv import load_dotenv

print("--- Checking Env Vars ---")
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
print(f"OPENAI_API_KEY: {'[FOUND]' if api_key else '[NOT FOUND]'}")

if not api_key:
    # Try loading from parent
    print("Trying load_dotenv('../.env')...")
    load_dotenv("../.env")
    api_key = os.getenv("OPENAI_API_KEY")
    print(f"OPENAI_API_KEY: {'[FOUND]' if api_key else '[NOT FOUND]'}")
