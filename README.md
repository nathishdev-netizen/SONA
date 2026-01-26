# SONA AI

**Socratic Navigator & Assessor**

SONA AI evaluates how well learners understand what they've learned through adaptive interrogation and data-driven evaluation.

## 🎯 Core Philosophy

SONA doesn't teach. It **interrogates, adapts, measures, and stops** when it has enough evidence of your understanding.

## 🌟 Features

- **Adaptive Questioning**: Multi-level questions that adjust to your understanding
- **Deep Evaluation**: Measures correctness, depth, and transfer ability
- **Multi-Source Learning**: Supports YouTube, websites, PDFs, and text
- **Voice Interaction**: Speak your answers naturally
- **Full Observability**: Powered by Opik for complete AI workflow transparency
- **Confidence-Based Stopping**: Ends when it has sufficient evidence, not after fixed questions

## 🏗️ Architecture

### Multi-Agent System (CrewAI)

- **Extractor Agent**: Processes learning materials from various sources
- **Interrogator Agent**: Generates adaptive questions based on your understanding
- **Evaluator Agent**: Scores answers across three dimensions
- **Conductor Agent**: Orchestrates the session and determines stopping points

### Tech Stack

**Backend**:
- Python 3.11+
- FastAPI
- CrewAI (Multi-agent orchestration)
- Opik (Observability, evaluation, optimization)
- Pinecone (Vector database)
- PostgreSQL (Session data)
- OpenAI / Groq (LLM providers)

**Voice**:
- OpenAI Whisper (Speech-to-Text)
- Piper TTS / Coqui (Text-to-Speech)

**Frontend**:
- Streamlit (MVP)
- Future: Next.js + React

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.11+
python --version

# PostgreSQL
brew install postgresql

# Redis (optional, for caching)
brew install redis
```

### Installation

```bash
# Clone repository
git clone <repository-url>
cd SONA

# Setup virtual environment
python -m venv venv
source venv/bin/activate

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your API keys

# Setup database
python scripts/setup_db.py

# Run backend
uvicorn src.main:app --reload

# In another terminal, run Streamlit frontend
cd ../frontend
pip install -r requirements.txt
streamlit run app.py
```

### Environment Variables

```env
# LLM Providers
OPENAI_API_KEY=your_key
GROQ_API_KEY=your_key

# Opik
OPIK_API_KEY=your_key
OPIK_WORKSPACE=sona-ai

# Vector Database
PINECONE_API_KEY=your_key
PINECONE_ENVIRONMENT=your_env
PINECONE_INDEX_NAME=sona-embeddings

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/sona

# Voice (optional)
WHISPER_MODEL=base
TTS_ENGINE=piper
```

## 📊 Understanding Evaluation

SONA evaluates your answers on three axes:

### 1. Correctness (0-100)
- Factual alignment with source material
- No hallucinations or fabricated information

### 2. Depth (0-100)
- Contextual understanding
- Explanation quality relative to question difficulty
- Short answers can score high for simple questions

### 3. Transfer (0-100)
- Application to new situations
- Identifying implications and consequences
- Demonstrating flexible understanding

**Final Score Formula**:
```
answer_score = 0.5 × correctness + 0.3 × depth + 0.2 × transfer
understanding_score = 0.6 × previous_understanding + 0.4 × answer_score
```

## 🔍 Opik Integration

SONA maximizes Opik for:

- **Tracing**: Every agent action and LLM call
- **Evaluation**: Custom evaluators for each scoring dimension
- **Metrics**: Understanding progression, question difficulty, session analytics
- **Guardrails**: Safety checks and content moderation
- **Gateway**: Unified LLM provider access
- **Prompt Library**: Versioned prompt management
- **Experiments**: A/B testing questioning strategies
- **Optimization**: Agent and prompt improvement

## 📁 Project Structure

```
SONA/
├── backend/          # FastAPI + CrewAI agents
├── frontend/         # Streamlit (MVP) / Next.js (future)
├── opik/            # Opik datasets, evaluators, experiments
├── mcp/             # Model Context Protocol servers
├── config/          # Configuration files
├── docs/            # Documentation
└── infrastructure/  # Docker, deployment configs
```

## 🛠️ Development

```bash
# Run tests
pytest backend/tests/

# Run with Opik tracing
python backend/scripts/test_opik.py

# Evaluate on test dataset
python backend/scripts/run_evaluation.py
```

## 📝 License

MIT

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

---

Built with ❤️ to help learners truly understand, not just consume.
