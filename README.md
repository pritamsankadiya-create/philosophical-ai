# 🧠 Philosophical AI

> *A conversational AI powered by the wisdom of 23 great philosophers — speaks English, Hindi & Hinglish!*

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)
![LangChain](https://img.shields.io/badge/LangChain-0.2-orange)
![Ollama](https://img.shields.io/badge/Ollama-Mistral-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📖 What is this?

**Philosophical AI** is a local AI chatbot that answers your life questions using the wisdom of the world's greatest philosophers — from ancient Greek thinkers like Socrates and Plato to Indian masters like Osho, Vivekananda and Shankaracharya.

Ask in **English**, **Hindi** or **Hinglish** — it understands all three!

---

## ✨ Features

- 🌊 **Streaming responses** — answers appear word by word like ChatGPT
- 🧠 **Conversation memory** — remembers your last 5 messages
- 🌍 **Multi-language** — English, Hindi and Hinglish support
- 🔍 **Semantic search** — finds the most relevant philosopher quotes
- 🪞 **Reflection engine** — improves every answer before showing it
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
│   ├── thinking_engine.py      ← Main AI brain
│   └── reflection_engine.py    ← Answer improvement engine
│
├── memory/
│   ├── vector_store.py         ← Chroma vector database
│   ├── chat_memory.py          ← Conversation memory
│   └── chroma_db/              ← Auto-generated vector DB
│
├── models/
│   └── llm_loader.py           ← Ollama / Groq connector
│
├── dataset/
│   └── philosophy.txt          ← 600+ philosopher quotes
│
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- [Ollama](https://ollama.com) installed

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

### 4. Pull AI model

```bash
ollama pull mistral
ollama pull nomic-embed-text
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
| `GET` | `/stream?question=...` | ⚡ Streaming response |
| `POST` | `/chat` | Normal response with memory |
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

---

## 🧠 How it Works

```
User Question
      │
      ▼
┌─────────────────┐
│ Language Detect │  ← English / Hindi / Hinglish?
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Translate       │  ← Hinglish → Hindi
│ Hinglish        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Vector Search   │  ← Find relevant philosopher quotes
│ (Chroma DB)     │     using semantic similarity
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Think Engine    │  ← Generate answer using Mistral
│ (Mistral LLM)   │     with relevant quotes + memory
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Reflect Engine  │  ← Improve the answer quality
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Stream to UI    │  ← Word by word like ChatGPT
└─────────────────┘
```

---

## 🔧 Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| Model | `mistral` | LLM model via Ollama |
| Embeddings | `nomic-embed-text` | Embedding model |
| Memory | `5 messages` | Conversation history limit |
| Chunk size | `150` | Vector DB chunk size |
| Max tokens | `300` | Response length |
| Temperature | `0.7` | AI creativity level |

---

## 🐳 Docker

```bash
# Build
docker build -t philosophical-ai .

# Run
docker run -p 8000:8000 philosophical-ai
```

---

## 📦 Requirements

```
fastapi
uvicorn
langchain
langchain-community
langchain-ollama
langchain-chroma
langchain-text-splitters
chromadb
requests
aiofiles
pydantic
```

---

## 🗺️ Roadmap

- [x] Level 1 — Rich philosophy knowledge base
- [x] Level 2 — Conversation memory
- [x] Level 2.5 — Hindi + Hinglish support
- [x] Level 3 — Streaming Chat UI
- [ ] Level 4 — Deploy online (Railway/Render)
- [ ] Level 5 — User accounts
- [ ] Level 6 — Save favorite quotes
- [ ] Level 7 — Daily wisdom notifications

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
| **LangChain** | AI orchestration |
| **Chroma DB** | Vector database |
| **Ollama** | Local LLM runner |
| **Mistral** | Language model |
| **nomic-embed-text** | Embeddings |
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
