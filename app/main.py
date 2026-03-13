# ============================================================
# 📁 app/main.py
# ✅ Complete — Streaming + Hindi fix + Chat UI!
# ============================================================

import sys
import os
import json as _json

# ✅ Path setup — must be before all other imports!
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_DIR  = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from fastapi import FastAPI
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from core.thinking_engine import think, translate_hinglish, detect_language, build_search_query
from core.reflection_engine import reflect
from memory.chat_memory import ChatMemory
from memory.vector_store import build_vector_store, search_philosophy
from models.llm_loader import generate_stream

app = FastAPI(title="🧠 Philosophical AI")

# ✅ Static files setup
STATIC_DIR = os.path.join(APP_DIR, "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# One memory for whole session
memory = ChatMemory(max_history=5)


class QuestionRequest(BaseModel):
    question: str


# ─── Routes ──────────────────────────────────────────────────

@app.get("/")
def home():
    """Serve Chat UI"""
    index_path = os.path.join(APP_DIR, "static", "index.html")
    try:
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    except FileNotFoundError:
        return HTMLResponse("""
            <h2>❌ index.html not found!</h2>
            <p>Make sure <b>app/static/index.html</b> exists</p>
        """)


@app.get("/health")
def health():
    return {
        "status"    : "✅ running",
        "model"     : "llama-3.3-70b-versatile",
        "streaming" : "✅ active",
        "memory"    : f"{len(memory.history)} messages"
    }


@app.post("/chat")
def chat(request: QuestionRequest):
    """Normal chat WITH memory"""
    question     = request.question
    first_answer = think(question, chat_memory=memory)
    final_answer = reflect(first_answer, question)

    memory.add_message("user", question)
    memory.add_message("ai", final_answer)

    return {
        "question"     : question,
        "answer"       : final_answer,
        "memory_count" : len(memory.history)
    }


@app.get("/stream")
async def stream_chat(question: str):
    """
    ⚡ Streaming endpoint — word by word like ChatGPT!
    Supports Hindi + English + Hinglish!
    """
    try:
        # Translate + detect language
        translated = translate_hinglish(question)
        language   = detect_language(question)

        # Smart search — uses memory to resolve vague follow-ups
        search_query = build_search_query(translated, memory)
        relevant = search_philosophy(search_query, top_k=3)
        context  = "\n".join([f"- {r}" for r in relevant])

        # Get history
        history = ""
        if len(memory.history) > 0:
            history = memory.get_history_as_text()

        # Build prompt
        if language == 'hindi':
            prompt = f"""तुम एक दार्शनिक गुरु हो।
नीचे दिए ज्ञान से प्रश्न का उत्तर दो।
केवल हिंदी में। 3-4 वाक्य। सीधे उत्तर दो।

ज्ञान:
{context}

पिछली बातचीत:
{history}

प्रश्न: {translated}

उत्तर:"""
        else:
            prompt = f"""You are a wise philosophical guru.
Answer ONLY the question using the knowledge below.
Give 3-4 sentences. Stay on topic. Be direct and deep.

Knowledge:
{context}

Previous conversation:
{history}

Question: {question}

Answer:"""

        # Collect full answer for memory
        full_answer = []

        def event_stream():
            try:
                for token in generate_stream(prompt):
                    full_answer.append(token)

                    # ✅ JSON encode to safely handle
                    # Hindi unicode in SSE stream!
                    encoded = _json.dumps(
                        token,
                        ensure_ascii=False
                    )
                    yield f"data: {encoded}\n\n"

                # Save to memory after complete
                memory.add_message("user", question)
                memory.add_message(
                    "ai",
                    "".join(full_answer)
                )

                # Done signal
                yield f"data: \"[DONE]\"\n\n"

            except Exception as e:
                yield f"data: \"❌ Error: {str(e)}\"\n\n"
                yield f"data: \"[DONE]\"\n\n"

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control"              : "no-cache",
                "X-Accel-Buffering"          : "no",
                "Access-Control-Allow-Origin": "*",
            }
        )

    except Exception as e:
        def error_stream():
            yield f"data: \"❌ Error: {str(e)}\"\n\n"
            yield f"data: \"[DONE]\"\n\n"

        return StreamingResponse(
            error_stream(),
            media_type="text/event-stream"
        )


@app.get("/history")
def get_history():
    return {
        "history"        : memory.history,
        "total_messages" : len(memory.history)
    }


@app.get("/clear")
def clear():
    memory.clear()
    return {"message": "🧹 Memory cleared!"}


@app.get("/rebuild")
def rebuild():
    build_vector_store()
    return {"message": "✅ Knowledge rebuilt!"}


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*45)
    print("🧠 Philosophical AI")
    print("⚡ Streaming like ChatGPT!")
    print("="*45)
    print("📍 URL  : http://localhost:8000")
    print("📖 Docs : http://localhost:8000/docs")
    print("="*45 + "\n")
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port
    )