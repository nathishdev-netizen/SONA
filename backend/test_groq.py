"""
Test Groq LLM Connection
Quick script to verify Groq API key is working
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.config import settings
from src.core.llm_config import llm_config


def test_groq():
    """Test Groq LLM connection"""
    
    print("🧪 Testing Groq LLM Connection...\n")
    
    # Check if API key is set
    if not settings.groq_api_key or settings.groq_api_key == "":
        print("❌ ERROR: GROQ_API_KEY not set in .env file")
        print("\nPlease add your Groq API key to backend/.env:")
        print("GROQ_API_KEY=gsk_your_actual_key_here")
        print("\nGet a free key at: https://console.groq.com")
        return False
    
    print(f"✅ Groq API key found (starts with: {settings.groq_api_key[:7]}...)")
    print(f"✅ Default provider: {settings.default_llm_provider}")
    print(f"✅ Model: {settings.groq_model}\n")
    
    try:
        # Get Groq LLM
        print("🔄 Connecting to Groq...")
        llm = llm_config.get_llm(provider="groq")
        
        # Test simple completion
        print("🔄 Sending test message...")
        response = llm.invoke("Say 'Groq is working!' and nothing else.")
        
        print("\n" + "="*50)
        print("✅ SUCCESS! Groq is working!")
        print("="*50)
        print(f"\nResponse: {response.content}")
        print("\n" + "="*50)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}\n")
        
        if "Invalid API Key" in str(e) or "401" in str(e):
            print("⚠️  API key is invalid or expired")
            print("   Get a new key at: https://console.groq.com")
        elif "rate limit" in str(e).lower():
            print("⚠️  Rate limit exceeded")
            print("   Wait a minute and try again")
        else:
            print("⚠️  Unexpected error occurred")
        
        return False


if __name__ == "__main__":
    print("\n" + "="*50)
    print("  SONA AI - Groq Connection Test")
    print("="*50 + "\n")
    
    success = test_groq()
    
    if success:
        print("\n✅ All tests passed! You're ready to use Groq with SONA AI!")
        print("\nNext steps:")
        print("1. Run the backend: uvicorn src.main:app --reload")
        print("2. Run the frontend: cd ../frontend && streamlit run app.py")
    else:
        print("\n❌ Test failed. Please fix the errors above and try again.")
        sys.exit(1)
