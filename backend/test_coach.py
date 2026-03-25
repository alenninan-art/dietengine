import requests
import json

# Note: This requires a valid token. Since I can't easily get one from here without logging in via API,
# I will temporarily add a bypass or check if I can use the existing server logs if I trigger a request from the UI.
# However, I can also try to hit the /diagnostics endpoint to check CORS and health.

url = "http://localhost:8000/chat"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer TEST_TOKEN" # This will fail unless I generate a real one
}

payload = {
    "message": "Generate a 3-day muscle gain workout plan for the gym. I have dumbbells and no injuries."
}

print(f"Testing AI Fitness Coach at {url}...")
# I'll just check if the server is up and responsive first.
try:
    resp = requests.get("http://localhost:8000/")
    print(f"Server Health: {resp.json()}")
except Exception as e:
    print(f"Server unreachable: {e}")
