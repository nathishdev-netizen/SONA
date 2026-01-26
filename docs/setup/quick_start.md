# Quick Start Guide

## Prerequisites for Running SONA

### Required API Keys

**Minimum to get started**:
- OpenAI API key (for LLM)

**Recommended** (can add later):
- Opik API key (for observability) - Free at [comet.com/opik](https://www.comet.com/opik)
- Pinecone API key (for vector DB) - Free at [pinecone.io](https://www.pinecone.io/)

### Setup Steps

1. **Set Environment Variables** in `backend/.env`:
   ```bash
   OPENAI_API_KEY=sk-your-key-here
   ```

2. **Install Dependencies**:
   ```bash
   source venv/bin/activate
   cd backend
   pip install -r requirements.txt
   ```

3. **Run Backend**:
   ```bash
   uvicorn src.main:app --reload
   ```

4. **Run Frontend** (in another terminal):
   ```bash
   cd frontend
   pip install -r requirements.txt
   streamlit run app.py
   ```

## Current Status

✅ Project structure created
✅ Virtual environment created
⏳ Awaiting API keys
⏳ Install dependencies
⏳ Run backend
⏳ Implement agents
