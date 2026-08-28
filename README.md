# 🧠 Philosophical AI

> *A conversational AI powered by the wisdom of 23 great philosophers — speaks English, Hindi & Hinglish!*

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)
![LangChain](https://img.shields.io/badge/LangChain-0.2-orange)
![Groq](https://img.shields.io/badge/Groq-Qwen_3.8_27B-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📖 What is this?

**Philosophical AI** is a cloud-powered AI chatbot that answers your life questions using the wisdom of the world's greatest philosophers — from ancient Greek thinkers like Socrates and Plato to Indian masters like Osho, Vivekananda and Shankaracharya.

It features a **15-stage cognitive pipeline** with Prajna (प्रज्ञा) pattern detection, response contracts, Navarasa emotion detection, and persistent learning — analyzing your question, detecting what you're NOT saying, retrieving relevant wisdom, composing context-aware prompts, and reflecting on its own answers.

Ask in **English**, **Hindi** or **Hinglish** — it understands all three!

---

## ✨ Features

- 🌊 **Streaming responses** — answers appear word by word like ChatGPT
- 🧠 **Cognitive Pipeline** — 15-stage processing: detect → analyze → Prajna insight → retrieve → compose → generate → contract enforce → reflect → remember
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
│   ├── pipeline.py             ← Central orchestrator (15-stage cognitive pipeline)
│   ├── concept_analyzer.py     ← Pure Python concept/theme/intent/Navarasa extraction
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
# Edit .env and add your Groq API key
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
| `GET` | `/stream?question=...` | ⚡ Streaming response (cognitive pipeline) |
| `POST` | `/chat` | Full pipeline response with reflection |
| `GET` | `/analyze?question=...` | 🔬 Debug: concept analysis without LLM call |
| `GET` | `/history` | View conversation history |
| `GET` | `/clear` | Clear conversation memory |
| `GET` | `/rebuild` | Rebuild vector database |
| `GET` | `/health` | Server health check |
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
  "translated": "What is karma according to Krishna",
  "language": "english",
  "concepts": ["karma"],
  "themes": ["gita_philosophy", "buddhism", "vedanta"],
  "philosophers": ["Shree Krishna"],
  "intent": "define",
  "question_depth": "standard"
}
```

---

## 🧠 How it Works — Cognitive Pipeline

```
User Question
      │
      ▼
┌─────────────────┐
│ Stage 1:        │  ← Detect English / Hindi / Hinglish
│ Language Detect  │     Translate Hinglish → Hindi
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Stage 2:        │  ← Extract concepts, themes, philosophers,
│ Concept Analyzer │     intent (define/compare/apply/challenge)
│ (Pure Python)   │     and question depth — NO LLM call
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Stage 3:        │  ← Multi-strategy search:
│ Knowledge       │     1. Direct question search
│ Retriever       │     2. Concept-enriched search
│ (Chroma DB)     │     3. Philosopher-specific search
└────────┬────────┘     + Vague follow-up resolution
         │
         ▼
┌─────────────────┐
│ Stage 4:        │  ← Embed reasoning frameworks (Vedanta,
│ Prompt Composer  │     Buddhism, Stoicism...) + dialectic
│                 │     structure + multi-perspective + intent
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Stage 5:        │  ← Generate answer using Qwen 3.8 27B
│ LLM Generation  │     via Groq API (streaming or full)
│ (Groq API)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Stage 6:        │  ← Intent-aware self-critique
│ Reflection      │     Deepens superficial answers
│ (GPT-OSS 20B) │     using a fast smaller model
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Stage 7:        │  ← Save to memory with concept metadata
│ Memory + Themes  │     Track recurring themes across turns
└─────────────────┘
```

---

## 🔧 Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| Model | `qwen/qwen3.8-27b` | LLM model via Groq |
| Fast Model | `llama-3.1-8b-instant` | Reflection engine model |
| Memory | `5 messages` | Conversation history limit |
| Max tokens | `800` | Response length (main) / `200` (reflection) |
| Temperature | `0.7` | AI creativity level |
| Top P | `0.9` | Nucleus sampling |

---

## 🐳 Docker

```bash
# Build
docker build -t philosophical-ai .

# Run (pass your Groq API key)
docker run -p 8000:8000 -e GROQ_API_KEY=your_key_here philosophical-ai
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

- [x] Level 1 — Rich philosophy knowledge base
- [x] Level 2 — Conversation memory
- [x] Level 2.5 — Hindi + Hinglish support
- [x] Level 3 — Streaming Chat UI
- [x] Level 4 — Cognitive Pipeline (concept analysis, multi-strategy retrieval, prompt composition)
- [x] Level 4.5 — Migrate to Groq API for cloud deployment
- [ ] Level 5 — Deploy online (Railway/Render)
- [ ] Level 6 — User accounts
- [ ] Level 7 — Save favorite quotes
- [ ] Level 8 — Daily wisdom notifications

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
| **LangChain** | Vector store & text splitting |
| **Chroma DB** | Vector database |
| **Groq API** | Cloud LLM inference |
| **Qwen 3.8 27B** | Main language model |
| **GPT-OSS 20B** | Fast reflection model |
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
