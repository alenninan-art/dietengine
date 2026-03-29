import os
import google.generativeai as genai
from dotenv import load_dotenv

def test_gemini():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env")
        return

    print(f"Testing Gemini with key: {api_key[:5]}...{api_key[-5:] if len(api_key) > 5 else ''}")
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hello, are you working? Respond with 'Yes, I am working!' if you are.")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error calling Gemini: {e}")

if __name__ == "__main__":
    test_gemini()
