"""
Run this script to see exactly which Gemini models work with your API key.
Usage: python check_models.py
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: GEMINI_API_KEY not found in .env file")
    exit(1)

print(f"Testing API key: {api_key[:8]}...")
print("=" * 50)

# Step 1: List all available models
print("\n[1] Fetching available models...")
r = requests.get(
    f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
)

if r.status_code != 200:
    print(f"FAILED to list models: {r.json()}")
    exit(1)

models = r.json().get("models", [])
generate_models = [
    m for m in models
    if "generateContent" in m.get("supportedGenerationMethods", [])
]

print(f"\nFound {len(generate_models)} models that support generateContent:\n")
for m in generate_models:
    print(f"  -> {m['name'].replace('models/', '')}")

# Step 2: Test the first working model
print("\n" + "=" * 50)
print("[2] Testing first available model...")

if generate_models:
    model_name = generate_models[0]["name"].replace("models/", "")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    test = requests.post(
        url,
        json={"contents": [{"role": "user", "parts": [{"text": "Say hello"}]}]}
    )
    if test.status_code == 200:
        reply = test.json()["candidates"][0]["content"]["parts"][0]["text"]
        print(f"\nSUCCESS! Model '{model_name}' works!")
        print(f"Response: {reply[:80]}")
        print(f"\n*** Use this model name in config.yaml: {model_name} ***")
    else:
        print(f"Test failed: {test.json()}")
else:
    print("No generateContent models found for this API key.")
    print("Your key may not have Gemini API access.")
    print("Create a new key at: https://aistudio.google.com/apikey")