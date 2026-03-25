import requests
import json

url = "http://localhost:8000/chat"
# We need a valid token to test. I'll just use a mock request if possible, 
# but the endpoint requires auth. 
# Alternatively, I'll temporarily disable auth on the endpoint for testing.

print(f"Testing {url}...")
try:
    # This will likely fail with 401, but we can see if it reaches the server.
    response = requests.post(url, json={"message": "Healthy snacks?"})
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
