import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

test_models = [
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-pro",
    "models/gemini-1.5-flash",
    "models/gemini-1.5-pro",
    "models/gemini-pro",
    "gemini-1.5-flash-latest",
    "gemini-1.5-pro-latest"
]

print("Testing each model name...\n")
for model_name in test_models:
    try:
        print(f"Trying: '{model_name}'")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say hi in one word")
        print(f"  ✅✅✅ SUCCESS! Use this: '{model_name}'")
        print(f"  Response: {response.text}\n")
        break
    except Exception as e:
        error_msg = str(e)[:120]
        print(f"  ❌ Failed: {error_msg}\n")
