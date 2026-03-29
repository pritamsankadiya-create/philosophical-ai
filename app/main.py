# ============================================================
# app/main.py
# FastAPI server with v3 cognitive pipeline
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
from core.pipeline import (
    run_pipeline, run_pipeline_stream, get_pipeline_metadata,
    get_latest_trace, get_all_traces, long_term_memory
)
from memory.chat_memory import ChatMemory
from memory.vector_store import build_vector_store
from models.llm_loader import get_model_stats

app = FastAPI(title="Philosophical AI")

# Static files setup
STATIC_DIR = os.path.join(APP_DIR, "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Short-term: conversation history (cleared by /clear)
memory = ChatMemory(max_history=5)

# Long-term memory is initialized in pipeline.py and imported above
# Track this server session
long_term_memory.increment_session()


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
    stats = get_model_stats()
    return {
        "status"         : "running",
        "version"        : "v3",
        "model"          : stats["current_model"],
        "model_stats"    : stats,
        "streaming"      : "active",
        "chat_memory"    : f"{len(memory.history)} messages",
        "long_term"      : f"{long_term_memory.total_questions} questions learned",
        "concepts_known" : len(long_term_memory.concept_counts),
    }


@app.post("/chat")
def chat(request: QuestionRequest):
    """Chat with v3 cognitive pipeline (2 LLM calls)"""
    question = request.question
    answer = run_pipeline(question, chat_memory=memory, use_reflection=True)

    return {
        "question"     : question,
        "answer"       : answer,
        "memory_count" : len(memory.history)
    }


@app.get("/stream")
async def stream_chat(question: str):
    """Streaming endpoint with v3 cognitive pipeline (1 LLM call)"""
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
    """Debug endpoint — shows v3 concept analysis without LLM call"""
    return get_pipeline_metadata(question)


@app.get("/trace")
def trace():
    """Get the latest flow trace — debug endpoint for v3"""
    return get_latest_trace()


@app.get("/traces")
def traces():
    """Get all stored flow traces"""
    return get_all_traces()


@app.get("/history")
def get_history():
    return {
        "history"        : memory.history,
        "total_messages" : len(memory.history)
    }


@app.get("/clear")
def clear():
    """Clear conversation history only. Long-term memory is preserved."""
    memory.clear()
    return {
        "message": "Chat history cleared!",
        "note": "Long-term memory preserved (concept patterns, learned themes, traces)",
        "long_term_stats": {
            "questions_learned": long_term_memory.total_questions,
            "concepts_tracked": len(long_term_memory.concept_counts),
        }
    }


@app.get("/clear-all")
def clear_all():
    """Nuclear reset — clears EVERYTHING including long-term memory."""
    memory.clear()
    long_term_memory.reset()
    return {
        "message": "ALL memory erased — chat history AND long-term learning",
        "warning": "The system has forgotten everything it learned"
    }


@app.get("/memory")
def get_memory():
    """View the system's long-term memory — what it has learned over time."""
    return long_term_memory.get_summary()


@app.get("/rebuild")
def rebuild():
    build_vector_store()
    return {"message": "Knowledge rebuilt!"}


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*45)
    print("Philosophical AI v3")
    print("Flow-Driven Cognitive Pipeline")
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
