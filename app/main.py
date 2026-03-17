# ============================================================
# app/main.py
# FastAPI server with cognitive pipeline
# ============================================================

import sys
import os
import json as _json

# Path setup — must be before all other imports!
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_DIR  = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from fastapi import FastAPI
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from core.pipeline import run_pipeline, run_pipeline_stream, get_pipeline_metadata
from memory.chat_memory import ChatMemory
from memory.vector_store import build_vector_store

app = FastAPI(title="Philosophical AI")

# Static files setup
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
            <h2>index.html not found!</h2>
            <p>Make sure <b>app/static/index.html</b> exists</p>
        """)


@app.get("/health")
def health():
    return {
        "status"    : "running",
        "model"     : "llama-3.3-70b-versatile",
        "streaming" : "active",
        "memory"    : f"{len(memory.history)} messages"
    }


@app.post("/chat")
def chat(request: QuestionRequest):
    """Chat with cognitive pipeline (2 LLM calls)"""
    question = request.question
    answer = run_pipeline(question, chat_memory=memory, use_reflection=True)

    return {
        "question"     : question,
        "answer"       : answer,
        "memory_count" : len(memory.history)
    }


@app.get("/stream")
async def stream_chat(question: str):
    """Streaming endpoint with cognitive pipeline (1 LLM call)"""
    try:
        def event_stream():
            try:
                for token in run_pipeline_stream(question, chat_memory=memory):
                    encoded = _json.dumps(token, ensure_ascii=False)
                    yield f"data: {encoded}\n\n"

                yield f"data: \"[DONE]\"\n\n"

            except Exception as e:
                yield f"data: \"Error: {str(e)}\"\n\n"
                yield f"data: \"[DONE]\"\n\n"

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control"              : "no-cache",
                "X-Accel-Buffering"          : "no",
                "Access-Control-Allow-Origin" : "*",
            }
        )

    except Exception as e:
        def error_stream():
            yield f"data: \"Error: {str(e)}\"\n\n"
            yield f"data: \"[DONE]\"\n\n"

        return StreamingResponse(
            error_stream(),
            media_type="text/event-stream"
        )


@app.get("/analyze")
def analyze(question: str):
    """Debug endpoint — shows concept analysis without LLM call"""
    return get_pipeline_metadata(question)


@app.get("/history")
def get_history():
    return {
        "history"        : memory.history,
        "total_messages" : len(memory.history)
    }


@app.get("/clear")
def clear():
    memory.clear()
    return {"message": "Memory cleared!"}


@app.get("/rebuild")
def rebuild():
    build_vector_store()
    return {"message": "Knowledge rebuilt!"}


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*45)
    print("Philosophical AI")
    print("Cognitive Pipeline Active")
    print("="*45)
    print("URL  : http://localhost:8000")
    print("Docs : http://localhost:8000/docs")
    print("="*45 + "\n")
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port
    )
