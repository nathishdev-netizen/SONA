# Using Groq with SONA AI

## Why Groq?

- ⚡️ **Blazing fast** inference (much faster than OpenAI)
- 🆓 **Free tier** with generous limits
- 🧠 **Great models**: Llama 3.3 70B, Mixtral, etc.
- 💰 **Cost effective** for development

## Setup Steps

### 1. Get Groq API Key

1. Visit [https://console.groq.com](https://console.groq.com)
2. Sign up / Log in
3. Go to **API Keys** section
4. Click **Create API Key**
5. Copy the key (starts with `gsk_`)

### 2. Update `.env` File

```bash
# In backend/.env
GROQ_API_KEY=gsk_your_actual_key_here
DEFAULT_LLM_PROVIDER=groq
```

### 3. That's it! 🎉

The system is already configured to use Groq. All agents will automatically use Groq LLM.

## Available Groq Models

Update `GROQ_MODEL` in `.env` to use different models:

```bash
# Recommended (default)
GROQ_MODEL=llama-3.3-70b-versatile  # Best balance

# Alternatives
GROQ_MODEL=llama-3.1-70b-versatile  # Previous version
GROQ_MODEL=llama-3.1-8b-instant     # Fastest, smaller
GROQ_MODEL=mixtral-8x7b-32768       # Good for reasoning
GROQ_MODEL=gemma2-9b-it             # Google's Gemma
```

## Switching Between Providers

### Option 1: Change Default in `.env`

```bash
# Use Groq for everything
DEFAULT_LLM_PROVIDER=groq

# Or use OpenAI for everything
DEFAULT_LLM_PROVIDER=openai
```

### Option 2: Override Per Agent (Advanced)

In agent code, you can specify provider:

```python
# Use Groq for this agent
self.llm = llm_config.get_llm(provider="groq")

# Use OpenAI for this agent
self.llm = llm_config.get_llm(provider="openai")

# Use specific model
self.llm = llm_config.get_llm(
    provider="groq",
    model="llama-3.1-8b-instant",
    temperature=0.5
)
```

## Testing Groq Connection

Create a test file to verify it works:

```python
# test_groq.py
from src.core.llm_config import llm_config

# Get Groq LLM
llm = llm_config.get_llm(provider="groq")

# Test it
response = llm.invoke("Say 'Groq is working!' in one sentence")
print(response.content)
```

Run it:
```bash
cd backend
source ../venv/bin/activate
python test_groq.py
```

## Rate Limits (Free Tier)

Groq free tier is generous:
- **Requests per minute**: 30
- **Requests per day**: 14,400
- **Tokens per minute**: 20,000

Perfect for development and testing!

## Troubleshooting

### Error: "Invalid API Key"
- Check your API key in `.env`
- Make sure it starts with `gsk_`
- No spaces or quotes around the key

### Error: "Rate limit exceeded"
- Wait a minute and try again
- Free tier has 30 requests/minute limit

### Want both OpenAI and Groq?
- Keep both API keys in `.env`
- Switch `DEFAULT_LLM_PROVIDER` as needed
- Or configure specific agents to use specific providers

---

**Pro Tip**: Use Groq for development (fast, free), then switch to OpenAI for production if needed!
