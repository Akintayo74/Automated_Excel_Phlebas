import os
from google import genai
from dotenv import load_dotenv

# Load env vars
load_dotenv()

def test_api():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("✗ No GEMINI_API_KEY found in .env")
        return

    print(f"→ Found API Key: {api_key[:5]}...{api_key[-5:]}")
    
    try:
        client = genai.Client(api_key=api_key)
        
        print("→ Sending test prompt to Gemini...")
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents="Reply with exactly the word 'WORKING'"
        )
        
        print(f"→ Response: {response.text.strip()}")
        
        if "WORKING" in response.text:
            print("✓ SUCCESS: Gemini API is working correctly!")
        else:
            print("⚠ WARNING: Unexpected response content.")
            
    except Exception as e:
        print(f"✗ ERROR: {e}")

if __name__ == "__main__":
    test_api()
