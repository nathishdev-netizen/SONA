# Opik Integration Guide

## Overview

SONA AI maximizes Opik's capabilities for complete observability, evaluation, and optimization of the multi-agent learning evaluation system.

## Features Used

### 1. **Tracing** 🔍

Every agent action, LLM call, and tool use is traced with Opik.

**Implementation**:
```python
from src.opik_integration.tracing import opik_integration

@opik_integration.track_agent(
    name="Interrogator",
    metadata={"agent_type": "question_generation"}
)
def generate_question(input_data):
    # Automatically traced
    pass
```

**What's Traced**:
- Agent inputs and outputs
- LLM prompts and completions
- Token usage and costs
- Execution time
- Error traces

### 2. **Evaluation** ✅

Custom evaluators for SONA's three-dimensional scoring system.

**Custom Evaluators**:
- `CorrectnessEvaluator` - Factual accuracy
- `DepthEvaluator` - Contextual understanding
- `TransferEvaluator` - Application ability

**Location**: `backend/src/opik_integration/evaluation.py`

```python
from opik.evaluation import evaluate

results = evaluate(
    dataset=test_dataset,
    task=evaluation_task,
    scoring_metrics=[correctness_evaluator, depth_evaluator, transfer_evaluator]
)
```

### 3. **Metrics** 📊

**Custom Metrics**:
- Understanding score progression
- Question difficulty distribution
- Average scores by question type
- Session completion rate
- Stopping reason distribution

**Implementation**: `backend/src/opik_integration/metrics.py`

### 4. **Guardrails** 🛡️

**Integrated Guardrails**:
- Toxicity detection (user answers)
- Jailbreak prevention (system prompts)
- PII detection (uploaded content)
- Content moderation (generated questions)

**Configuration**: `config/guardrails.yaml`

```yaml
guardrails:
  enabled: true
  toxicity:
    threshold: 0.7
    action: reject
  jailbreak:
    enabled: true
    action: log_and_reject
  pii:
    enabled: true
    mask: true
```

### 5. **LLM Gateway** 🌐

Opik LLM Gateway provides unified access to multiple LLM providers.

**Configuration**:
```python
from src.opik_integration.gateway import opik_gateway

# Unified interface for OpenAI and Groq
llm = opik_gateway.get_llm(
    provider="openai",
    model="gpt-4o-mini"
)
```

**Benefits**:
- Automatic tracing
- Cost tracking
- Load balancing
- Caching

### 6. **Prompt Library** 📚

Centralized prompt management with versioning.

**Structure**:
```
opik/prompts/
├── interrogator_v1.yaml
├── interrogator_v2.yaml
├── evaluator_v1.yaml
└── versions/
```

**Usage**:
```python
from src.opik_integration.prompts import get_prompt

prompt = get_prompt("interrogator", version="v2")
```

### 7. **Experiments** 🧪

A/B testing different questioning strategies.

**Example Experiments**:
- Socratic vs. Direct questioning
- Aggressive vs. Friendly tone impact
- Difficulty adaptation algorithms
- Stopping threshold optimization

**Configuration**: `opik/experiments/`

```python
from opik import Experiment

experiment = Experiment(
    name="stopping_threshold_test",
    variants={
        "control": {"threshold": 0.85},
        "variant_a": {"threshold": 0.90},
        "variant_b": {"threshold": 0.80}
    }
)
```

### 8. **Agent Optimizer** ⚡

Automated prompt and agent optimization.

**Usage**:
```python
from src.opik_integration.optimizer import optimize_agent

optimized_prompt = optimize_agent(
    agent_name="interrogator",
    dataset=validation_dataset,
    metrics=["question_quality", "diversity"],
    trials=10
)
```

### 9. **Dashboards** 📈

Real-time monitoring and analytics.

**Key Dashboards**:
1. **Session Dashboard**: Active sessions, completion rate
2. **Agent Performance**: Execution time, success rate
3. **Evaluation Dashboard**: Score distributions, trends
4. **Cost Dashboard**: Token usage, API costs

**Configuration**: `opik/dashboards/sona_dashboard.json`

## Setup Instructions

### 1. Install Opik

```bash
pip install opik
```

### 2. Configure API Key

```bash
# In .env file
OPIK_API_KEY=your_api_key
OPIK_WORKSPACE=sona-ai
OPIK_PROJECT_NAME=sona-evaluation
```

### 3. Initialize Opik

```python
import opik

opik.configure(
    api_key="your_api_key",
    workspace="sona-ai"
)
```

### 4. Start Tracing

Tracing is automatic when using the `@track_agent` decorator.

### 5. View Traces

```bash
# Open Opik dashboard
opik ui
# Or visit: https://www.comet.com/opik
```

## Best Practices

1. **Tag Everything**: Use metadata to tag sessions, users, experiments
2. **Sample Production**: Don't trace 100% in production, sample strategically
3. **Alert on Anomalies**: Set up alerts for unusual patterns
4. **Review Weekly**: Analyze traces weekly for optimization opportunities
5. **Version Prompts**: Always version prompts for reproducibility

## Troubleshooting

### Traces Not Appearing

```python
# Check Opik configuration
from src.core.config import settings
print(settings.opik_api_key)  # Should not be empty
```

### High Latency

```python
# Use async tracing
import opik
opik.configure(async_mode=True)
```

### Cost Concerns

```python
# Add sampling
@track_agent(sample_rate=0.1)  # Trace 10%
def my_function():
    pass
```

---

For more details, see [Opik Documentation](https://www.comet.com/docs/opik)
