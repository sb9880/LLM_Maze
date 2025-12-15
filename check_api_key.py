"""Quick test to verify OpenAI API key is working."""

import os
import sys

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Try loading from llm_maze_research/.env
    env_path = os.path.join(os.path.dirname(__file__), 'llm_maze_research', '.env')
    load_dotenv(env_path)
    print(f"✓ Loaded .env file from: {env_path}")
except ImportError:
    print("⚠️  python-dotenv not installed, checking environment variables...")

print("\n" + "="*60)
print("OPENAI API KEY CHECK")
print("="*60 + "\n")

# Check if API key is set
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("❌ ERROR: OPENAI_API_KEY is not set!\n")
    print("Please set it by either:")
    print("  1. Edit llm_maze_research/.env and add: OPENAI_API_KEY=your-key")
    print("  2. Or run: export OPENAI_API_KEY=your-key (Mac/Linux)")
    print("  3. Or run: set OPENAI_API_KEY=your-key (Windows)\n")
    sys.exit(1)

# Mask the key for security (show only first/last few chars)
if len(api_key) > 10:
    masked_key = f"{api_key[:7]}...{api_key[-4:]}"
else:
    masked_key = "***"

print(f"✓ API Key found: {masked_key}")
print(f"  Length: {len(api_key)} characters")
print(f"  Starts with: {api_key[:7]}")
print()

# Try to make a test API call
print("-"*60)
print("Testing OpenAI API connection...")
print("-"*60)
print()

try:
    from openai import OpenAI

    client = OpenAI(api_key=api_key)

    print("Sending test request to OpenAI...")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "Say 'API works!' and nothing else."}
        ],
        max_tokens=10,
        temperature=0
    )

    result = response.choices[0].message.content

    print()
    print("="*60)
    print("✅ SUCCESS! OpenAI API is working!")
    print("="*60)
    print(f"\nResponse from GPT-3.5-turbo: {result}")
    print(f"\nTokens used:")
    print(f"  - Prompt: {response.usage.prompt_tokens}")
    print(f"  - Completion: {response.usage.completion_tokens}")
    print(f"  - Total: {response.usage.total_tokens}")
    print()
    print("="*60)
    print("You're ready to run experiments! 🎉")
    print("="*60)
    print()
    print("Next steps:")
    print("  1. Run: python test_conversation_memory.py")
    print("  2. Or start dashboard: uvicorn api.main:app --port 8000")
    print()

except Exception as e:
    print()
    print("="*60)
    print("❌ ERROR: API call failed!")
    print("="*60)
    print(f"\nError: {e}\n")

    if "authentication" in str(e).lower() or "api key" in str(e).lower():
        print("Possible issues:")
        print("  - API key is invalid or expired")
        print("  - API key doesn't have correct permissions")
        print("  - Get a new key at: https://platform.openai.com/api-keys")
    elif "billing" in str(e).lower() or "quota" in str(e).lower():
        print("Possible issues:")
        print("  - No payment method on file")
        print("  - Free credits exhausted")
        print("  - Check billing: https://platform.openai.com/account/billing")
    else:
        print("Possible issues:")
        print("  - Check internet connection")
        print("  - OpenAI API might be down")
        print("  - Verify API key at: https://platform.openai.com/api-keys")

    print()
    sys.exit(1)
