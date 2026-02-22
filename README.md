# 🎯 CareerAI — Production-Ready Career Advisor Chatbot

> A **domain-specific AI chatbot** built with Google Gemini GenAI API, Streamlit, and deployed on AWS EC2.
> Designed to production-grade standards: modular architecture, secure secrets management, robust error handling, and scalable deployment.

---

## 📋 Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Project Structure](#project-structure)
- [Local Setup](#local-setup)
- [Cloud Deployment (AWS EC2)](#cloud-deployment-aws-ec2)
- [Configuration](#configuration)
- [Prompt Engineering](#prompt-engineering)
- [Testing](#testing)

---

## Overview

**CareerAI** is a conversational career advisor powered by **Google Gemini 1.5 Flash**. It provides:
- Resume writing & ATS optimization
- Job search strategies
- Interview preparation (STAR method)
- Salary negotiation tactics
- Career transition guidance
- LinkedIn profile optimization

**Domain:** Career Advisory  
**UI:** Streamlit  
**Backend:** Python modular architecture  
**Cloud:** AWS EC2 (Ubuntu 24.04)

---

## Architecture

```
User Input
   │
   ▼
┌─────────────────────────┐
│  Streamlit UI Layer      │  ← src/ui/chat_interface.py
│  (chat_interface.py)     │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  Session Manager         │  ← src/utils/session.py
│  (multi-turn memory)     │  Maintains chat history per session
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  Prompt Engineering      │  ← src/prompts/career_prompts.py
│  (career_prompts.py)     │  System prompts, role constraints
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  Gemini API Handler      │  ← src/api/gemini_handler.py
│  (gemini_handler.py)     │  Auth, retry logic, token tracking
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  Google Gemini API       │  gemini-1.5-flash model
│  (Cloud)                 │
└─────────────────────────┘
```

### Module Responsibilities

| Module | Responsibility |
|--------|---------------|
| `app.py` | Entry point; loads config, launches UI |
| `src/api/gemini_handler.py` | All Gemini API interactions, error handling, retries |
| `src/prompts/career_prompts.py` | Centralized prompt templates and system instructions |
| `src/ui/chat_interface.py` | Streamlit UI rendering and event handling |
| `src/utils/session.py` | Multi-turn conversation memory management |
| `src/utils/config.py` | Config loading, env var management |
| `src/utils/logger.py` | Centralized logging (console + file) |
| `config.yaml` | All configurable parameters (no hardcoded values) |

---

## Features

### ✅ Production Standards Met

- **🔐 Secure API Key Management** — env vars only, never hardcoded; `.env.example` provided
- **🧠 Multi-Turn Memory** — full conversation history with configurable window size
- **⚡ Advanced Prompt Engineering** — structured system prompt with role constraints, domain limits, and response format guidelines
- **🏗️ Clean Architecture** — strict separation of concerns across modules
- **🔄 Error Handling & Fallbacks** — retry with exponential backoff, graceful degradation
- **📊 Token Usage Tracking** — logged per request, displayed in UI
- **📝 Structured Logging** — to console and file (`logs/app.log`)
- **☁️ Cloud Deployment** — systemd service on EC2 with auto-restart
- **🧪 Unit Tests** — comprehensive tests for all modules

---

## Project Structure

```
careerai-chatbot/
├── app.py                      # Entry point
├── config.yaml                 # All configuration (no hardcoded values)
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── deploy_ec2.sh               # One-command EC2 deployment
├── src/
│   ├── api/
│   │   └── gemini_handler.py   # Gemini API: auth, calls, retries, tokens
│   ├── prompts/
│   │   └── career_prompts.py   # System prompts, templates, domain constraints
│   ├── ui/
│   │   └── chat_interface.py   # Streamlit UI rendering
│   └── utils/
│       ├── config.py           # Config loading + env var overrides
│       ├── logger.py           # Centralized logging setup
│       └── session.py          # Multi-turn memory management
├── tests/
│   └── test_chatbot.py         # Unit tests (pytest)
├── logs/                       # Auto-created, app logs written here
└── docs/
    └── architecture.md         # Extended architecture notes
```

---

## Local Setup

### Prerequisites
- Python 3.11+
- Google Gemini API key ([get one here](https://aistudio.google.com/apikey))

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/careerai-chatbot.git
cd careerai-chatbot

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY:
#   GEMINI_API_KEY=your_actual_api_key_here

# 5. Run the application
streamlit run app.py

# App will be available at: http://localhost:8501
```

---

## Cloud Deployment (AWS EC2)

### EC2 Setup (AWS Console)

1. **Launch EC2 Instance:**
   - AMI: `Ubuntu Server 24.04 LTS`
   - Instance type: `t3.small` (recommended) or `t2.micro` (free tier)
   - Key pair: create or use existing

2. **Configure Security Group:**
   | Type | Protocol | Port | Source |
   |------|----------|------|--------|
   | SSH | TCP | 22 | Your IP |
   | Custom TCP | TCP | **8501** | 0.0.0.0/0 |

3. **Connect to Instance:**
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-public-ip
   ```

### Automated Deployment

```bash
# Upload and run the deployment script
scp -i your-key.pem deploy_ec2.sh ubuntu@your-ec2-ip:~/
ssh -i your-key.pem ubuntu@your-ec2-ip
chmod +x deploy_ec2.sh
./deploy_ec2.sh
```

The script will:
- Install Python 3.11 and dependencies
- Clone the repository
- Set up virtualenv and install packages
- Configure your API key
- Create a **systemd service** (auto-start on reboot, auto-restart on crash)

### Access Your Chatbot
```
http://YOUR_EC2_PUBLIC_IP:8501
```

### Service Management
```bash
sudo systemctl status careerai    # Check status
sudo systemctl restart careerai   # Restart
sudo journalctl -u careerai -f    # View live logs
```

---

## Configuration

All configurable parameters are in `config.yaml`. Override any value via environment variables.

```yaml
gemini:
  model: "gemini-1.5-flash"       # Model to use
  max_output_tokens: 1024          # Max response length
  temperature: 0.7                 # Response creativity (0-1)

conversation:
  max_history_turns: 20            # Context window size

ui:
  show_token_usage: true           # Display token counts
  show_session_info: true          # Show session metadata
```

**Environment variable overrides:**
```bash
GEMINI_MODEL=gemini-1.5-pro       # Use Pro model
MAX_OUTPUT_TOKENS=2048             # Longer responses
LOG_LEVEL=DEBUG                    # Verbose logging
```

---

## Prompt Engineering

The system prompt in `src/prompts/career_prompts.py` implements:

1. **Persona Definition** — Expert career advisor with 15+ years experience
2. **Expertise Areas** — Explicit list of domains the bot handles
3. **Behavioral Rules** — How to respond, ask clarifying questions, format output
4. **Domain Constraints** — Hard boundary: only career topics; graceful redirect for off-topic
5. **Response Format** — Numbered lists for steps, bullets for options, concise answers
6. **Tone Guidelines** — Professional, warm, encouraging

**Reusable Templates:**
```python
from src.prompts.career_prompts import build_resume_prompt, build_interview_prep_prompt

# Generate a resume review prompt
prompt = build_resume_prompt(resume_text="...")

# Generate interview prep prompt
prompt = build_interview_prep_prompt(
    job_title="Software Engineer",
    company="Google",
    background="5 years Python experience"
)
```

---

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src --cov-report=term-missing
```

**Test Coverage:**
- Session creation, message management, history truncation, API format
- Prompt templates: content validation, template variable substitution
- Config: loading, env var overrides, missing API key handling
- API handler: success path, error handling, fallback responses

---

## 📊 Sample Conversation

```
User: I'm a software engineer with 3 years experience wanting to transition to product management.

CareerAI: Great goal! Here's a roadmap for your transition:

1. Build product intuition — take a PM course (e.g., Reforge, Product School)
2. Leverage your technical background — it's a huge differentiator in PM roles
3. Get APM/PM adjacent experience — lead a feature at your current job, contribute to roadmap discussions
4. Network intentionally — connect with PMs at target companies on LinkedIn
5. Prepare your narrative — frame your eng background as an asset, not a liability

Which area would you like to dive deeper into first?
```

---

*Built following production AI engineering standards — modular, secure, observable, and deployable.*
