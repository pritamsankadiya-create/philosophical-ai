# 🧠 Pragya — Philosophical AI

> *A conversational AI powered by the wisdom of 23 great philosophers — speaks English, Hindi & Hinglish!*

![Version](https://img.shields.io/badge/Version-4.1-a78bfa)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)
![Groq](https://img.shields.io/badge/Groq-Qwen_3.8_27B-purple)
![Jev](https://img.shields.io/badge/Jev--1.13-Crisis_Detection-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📖 What is this?

**Pragya** is a cloud-powered philosophical AI that answers your life questions using the wisdom of the world's greatest philosophers — from ancient Greek thinkers like Socrates and Plato to Indian masters like Osho, Vivekananda and Shankaracharya.

It features a **17-stage cognitive pipeline** with Jev-1.13 crisis detection, Prajna (प्रज्ञा) pattern detection, response contracts, Navarasa emotion detection, and persistent learning — analyzing your question, detecting crisis signals, detecting what you're NOT saying, retrieving relevant wisdom, composing context-aware prompts, and reflecting on its own answers.

Ask in **English**, **Hindi** or **Hinglish** — it understands all three!

---

## ✨ Features

- 🌊 **Streaming responses** — answers appear word by word like ChatGPT
- 🎯 **Jev Crisis Detection** — Jev-1.13 via OpenRouter detects crisis signals in Hindi/Hinglish with 97% accuracy (~870ms, $0.000017/call)
- 🧠 **Cognitive Pipeline** — 17-stage processing: detect → analyze → Jev crisis check → Prajna insight → retrieve → compose → generate → contract enforce → reflect → remember
- 🔬 **Concept Analyzer** — extracts philosophical concepts, themes, intent & depth from your question (pure Python, no LLM call)
- 🔍 **Multi-strategy retrieval** — concept-enriched + philosopher-specific + vague query resolution
- 📝 **Prompt Composer** — embeds reasoning frameworks + dialectic structure into prompts based on detected themes
- 🪞 **Intent-aware Reflection** — self-critique engine that deepens answers based on question intent (define, compare, apply, challenge)
- 💬 **Conversation themes** — tracks recurring concepts across turns to influence future responses
- 🌍 **Multi-language** — English, Hindi and Hinglish support
- 💬 **Beautiful Chat UI** — dark themed, mobile friendly
- ⏳ **Loading messages** — shows progress while AI is thinking
- 📚 **600+ quotes** from 23 philosophers

---

## 🏛️ Philosophers Included

| Category | Philosophers |
|----------|-------------|
| **Ancient Greek** | Socrates, Plato, Aristotle |
| **Ancient Eastern** | Confucius, Laozi |
| **Medieval** | Thomas Aquinas, Augustine of Hippo |
| **Modern Western** | Descartes, Locke, Kant, Hume, Rousseau, Marx, Nietzsche |
| **Contemporary** | Bertrand Russell, Sartre, Albert Camus |
| **Indian Masters** | Buddha, Shankaracharya, Vivekananda, Osho, Kalam, Chanakya, Kabir, Tagore, Patanjali, Guru Nanak, Krishna |
| **Sufi / Stoic** | Rumi, Marcus Aurelius, Gandhi |

---

## 🖥️ Demo

```
You  → What is consciousness?
AI   → Consciousness, as described by Shankaracharya, is pure
        awareness — the eternal self that transcends birth and
        death. It is not something you acquire but what you
        already are. Patanjali teaches that when the mind
        becomes completely still, pure consciousness shines
        forth like the sun behind clouds.

You  → चेतना क्या है?
AI   → चेतना वह शुद्ध जागरूकता है जो सदा विद्यमान रहती है।
        शंकराचार्य के अनुसार, ब्रह्म ही एकमात्र सत्य है और
        चेतना उसी का स्वरूप है।

You  → Pyar kya hai?
AI   → प्यार एक अवस्था है, कोई रिश्ता नहीं — ओशो ने यही सिखाया।
```

---

## 🗂️ Project Structure

```
philosophical-ai/
│
├── app/
│   ├── main.py                 ← FastAPI server (entry point)
│   └── static/
│       └── index.html          ← Chat UI (dark theme)
│
├── core/
│   ├── pipeline.py             ← Central orchestrator (17-stage cognitive pipeline)
│   ├── concept_analyzer.py     ← Pure Python concept/theme/intent/Navarasa extraction
│   ├── jev_classifier.py       ← Jev-1.13 crisis detection via OpenRouter API
│   ├── prajna_layer.py         ← Prajna (प्रज्ञा) — detects what is NOT said
│   ├── flow_engine.py          ← Soul identity + prompt composition + FlowTrace
│   ├── knowledge_retriever.py  ← Multi-strategy retrieval + vague query resolution
│   ├── thinking_engine.py      ← Language detection & Hinglish translation
│   ├── reflection_engine.py    ← Intent-aware self-critique + rhythm detection
│   ├── response_synthesizer.py ← Response assembly + trace building
│   ├── uncertainty_engine.py   ← Epistemic status classification
│   └── system_awareness.py     ← Meta-observation generation
│
├── utils/
│   ├── response_contract.py    ← Declarative response contracts (crisis/emotional/default)
│   └── phrase_dedup.py         ← Banned phrase stripping + 3-gram dedup
│
├── memory/
│   ├── vector_store.py         ← Chroma vector database
│   ├── chat_memory.py          ← Conversation memory
│   ├── long_term_memory.py     ← Persistent learning (concepts, depth boost)
│   └── chroma_db/              ← Auto-generated vector DB
│
├── models/
│   └── llm_loader.py           ← Groq API connector (Qwen 3.8 27B + fallback)
│
├── dataset/
│   ├── philosophy.txt          ← 600+ philosopher quotes
│   ├── scientific.txt          ← Neuroscience, psychology, cognitive science
│   ├── experiential.txt        ← Lived wisdom on suffering, love, fear
│   └── sanskrit_wisdom.txt     ← Rasa-tagged bilingual wisdom (unwired)
│
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- [Groq API Key](https://console.groq.com) (free tier available)
- [OpenRouter API Key](https://openrouter.ai) (optional — for Jev crisis detection)

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/philosophical-ai.git
cd philosophical-ai
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Linux / Mac
# venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
# Edit .env and add your API keys:
# GROQ_API_KEY=your_groq_key (required)
# JEV_API_KEY=your_openrouter_key (optional — enables Jev crisis detection)
```

### 5. Run the server

```bash
python app/main.py
```

### 6. Open in browser

```
http://localhost:8000
```

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Chat UI |
| `GET` | `/stream?question=...` | ⚡ Streaming response (primary endpoint) |
| `POST` | `/chat` | Full pipeline with reflection (2 LLM calls) |
| `GET` | `/analyze?question=...` | 🔬 Debug: concept analysis + Jev vs Python comparison + Prajna |
| `GET` | `/trace` | Latest flow trace (Jev, Prajna, contract, model info) |
| `GET` | `/traces` | All flow traces |
| `GET` | `/history` | View conversation history |
| `GET` | `/clear` | Clear conversation memory |
| `GET` | `/clear-all` | Nuclear reset: all memory erased |
| `GET` | `/memory` | View long-term learning data |
| `GET` | `/model-stats` | Model usage + fallback monitoring |
| `GET` | `/rebuild` | Rebuild vector database |
| `GET` | `/health` | Server health check (model stats + Jev stats) |
| `GET` | `/docs` | API documentation |

---

## 💬 Example API Usage

**Streaming (recommended):**
```javascript
const response = await fetch('/stream?question=What is karma?');
// Returns word-by-word stream
```

**Normal POST:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is love?"}'
```

**Response:**
```json
{
  "question": "What is love?",
  "answer": "Love, as Osho taught, is not a relationship but a state of being...",
  "memory_count": 2
}
```

**Concept Analysis (debug):**
```bash
curl "http://localhost:8000/analyze?question=What+is+karma+according+to+Krishna"
```

**Response:**
```json
{
  "question": "What is karma according to Krishna",
  "language": "english",
  "concepts": ["karma"],
  "themes": ["gita_philosophy", "buddhism", "vedanta"],
  "philosophers": ["Shree Krishna"],
  "intent": "define",
  "depth_score": 0.55,
  "question_type": "philosophical",
  "emotional_intensity": "low",
  "detected_rasa": "shaant",
  "prajna_hint": "",
  "contract_type": "default",
  "python_classification": { "question_type": "philosophical", "emotional_intensity": "low" },
  "jev_classification": { "crisis_signal": 0.02, "emotional_intensity": "low", "rasa": "shaant" }
}
```

---

## 🧠 How it Works — Cognitive Pipeline

```
User Question
      │
      ▼
┌─────────────────┐
│ Language Detect  │  ← Detect English / Hindi / Hinglish
│ + Translation   │     Translate Hinglish → Hindi (370+ words)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Concept Analyzer │  ← Extract concepts, themes, philosophers,
│ + Navarasa      │     intent, depth, emotional intensity,
│ (Pure Python)   │     9 rasas — NO LLM call
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Jev Crisis      │  ← Jev-1.13 via OpenRouter (~870ms)
│ Detection       │     crisis_signal 0.0–1.0
│ (API call)      │     ≥ 0.7 → force crisis contract
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Prajna Layer    │  ← Detect what is NOT said:
│ (प्रज्ञा)        │     displacement, circling, rasa-stuck,
│                 │     crisis signals, absence patterns
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Knowledge       │  ← Multi-strategy search across 3 layers:
│ Retriever       │     philosophical + scientific + experiential
│ (ChromaDB)      │     + long-term memory context hints
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Prompt Composer  │  ← Soul identity + rasa hints + warmth_first
│ (Flow Engine)   │     + philosophical opening + style mode
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ LLM Generation  │  ← Qwen 3.8 27B via Groq API
│ (Groq API)      │     Multi-tier fallback chain
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Contract        │  ← Jev crisis ≥ 0.7 OR Prajna crisis
│ Enforcement     │     → 3 sentences, strip advice
│                 │     emotional_high: 5 / default: 8
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Reflection      │  ← Self-critique: disclaimer check,
│ (Optional)      │     repetition, rhythm, paradox resolution
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Memory Update   │  ← Long-term learning + chat history
│ + Prajna History│     + Prajna question/rasa tracking
└─────────────────┘
```

---

## 🔧 Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| Main Model | `qwen/qwen3.8-27b` | Primary LLM via Groq (2M TPD) |
| Mid Fallback | `openai/gpt-oss-120b` | Tier 2 fallback on rate limit |
| Fast Fallback | `openai/gpt-oss-20b` | Tier 3 fallback |
| Crisis Detection | `typesafe/jev-1.13` | Jev via OpenRouter (~870ms, $0.000017/call) |
| Jev Timeout | `2 seconds` | Fail fast → Python fallback |
| Crisis Threshold | `≥ 0.7` | crisis_signal score to force crisis contract |
| Memory | `5 messages` | Short-term conversation history |
| Max tokens | `500–1680` | Adaptive based on depth + language |
| Temperature | `0.7` | AI creativity level |
| Crisis contract | `3 sentences` | Triggered by Jev ≥ 0.7 or Prajna crisis |
| Emotional contract | `5 sentences` | Max response for high distress |
| Default contract | `8 sentences` | Standard response length |

---

## 🐳 Docker

```bash
# Build
docker build -t philosophical-ai .

# Run (pass your API keys)
docker run -p 8000:8000 -e GROQ_API_KEY=your_key -e JEV_API_KEY=your_openrouter_key philosophical-ai
```

---

## 📦 Requirements

```
fastapi
uvicorn
groq
langchain-core
langchain-community
langchain-chroma
langchain-text-splitters
chromadb
onnxruntime
tokenizers
numpy
```

---

## 🗺️ Roadmap

- [x] Level 1 — Rich philosophy knowledge base (600+ quotes, 23 philosophers)
- [x] Level 2 — Conversation memory (short-term + long-term persistent learning)
- [x] Level 2.5 — Hindi + Hinglish support (370+ word translation dictionary)
- [x] Level 3 — Streaming Chat UI (dark theme, SSE, mobile responsive)
- [x] Level 4 — Cognitive Pipeline (17-stage: concept analysis, Navarasa, retrieval, prompt composition)
- [x] Level 4.5 — Groq API migration (Qwen 3.8 27B + multi-tier fallback)
- [x] Level 5 — Prajna layer (displacement, circling, rasa-stuck, crisis detection)
- [x] Level 6 — Response contracts (crisis/emotional/default sentence caps + enforcement)
- [x] Level 7 — Deploy on Render.com (Docker, auto-deploy from main)
- [x] Level 8 — Jev-1.13 crisis detection (97% accuracy, Hindi/Hinglish, $0.000017/call)
- [ ] Level 9 — Session isolation (per-user memory)
- [ ] Level 10 — Fine-tuning data collection
- [ ] Level 11 — Voice layer

---

## 🙏 Philosophy Sources

This project draws wisdom from:

- **Bhagavad Gita** — Krishna's teachings
- **Yoga Sutras** — Patanjali
- **Advaita Vedanta** — Shankaracharya
- **Buddhist Teachings** — Gautam Buddha
- **Sufi Poetry** — Rumi
- **Stoic Philosophy** — Marcus Aurelius
- **Existentialism** — Sartre, Camus
- **Indian Wisdom** — Osho, Vivekananda, Kalam, Chanakya, Kabir
- **Greek Philosophy** — Socrates, Plato, Aristotle
- **Taoism** — Laozi

---

## 👨‍💻 Built With

| Technology | Purpose |
|------------|---------|
| **FastAPI** | Backend API server |
| **ChromaDB + ONNX** | Vector database + embeddings |
| **Groq API** | Cloud LLM inference |
| **Qwen 3.8 27B** | Main language model |
| **GPT-OSS 20B** | Fallback model |
| **Jev-1.13 (TypeSafe)** | Crisis detection via OpenRouter |
| **HTML/CSS/JS** | Chat frontend |

---

## 📄 License

MIT License — feel free to use, modify and share!

---

## 🤝 Contributing

Pull requests are welcome! For major changes please open an issue first.

---

<div align="center">

**Made with 🧘 and philosophical curiosity**

*"The unexamined life is not worth living." — Socrates*

</div>
