# ============================================================
# memory/vector_store.py
# ChromaDB with built-in ONNX embeddings (no Ollama needed)
# v3: supports 3 knowledge layers with metadata tagging
# ============================================================

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_core.embeddings import Embeddings

# Absolute paths so it works from any working directory
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_PATH = os.path.join(_BASE_DIR, "memory", "chroma_db")

# v3: 3 knowledge layers
DATASET_FILES = {
    "philosophical": os.path.join(_BASE_DIR, "dataset", "philosophy.txt"),
    "scientific": os.path.join(_BASE_DIR, "dataset", "scientific.txt"),
    "experiential": os.path.join(_BASE_DIR, "dataset", "experiential.txt"),
}

# Backward compat
DATASET_PATH = DATASET_FILES["philosophical"]


class ChromaDefaultEmbeddings(Embeddings):
    """Wraps ChromaDB's built-in ONNX embedding (all-MiniLM-L6-v2) for LangChain."""

    def __init__(self):
        from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
        self._ef = DefaultEmbeddingFunction()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._ef(texts)

    def embed_query(self, text: str) -> list[float]:
        return self._ef([text])[0]


def get_embeddings():
    """Load embedding model — uses ChromaDB's built-in ONNX model."""
    return ChromaDefaultEmbeddings()


def _load_and_clean(file_path: str) -> str:
    """Load a text file and remove comment/header lines."""
    loader = TextLoader(file_path)
    documents = loader.load()
    clean_lines = []
    for doc in documents:
        for line in doc.page_content.split('\n'):
            stripped = line.strip()
            if stripped and not stripped.startswith('#') and not stripped.startswith('\u2500'):
                clean_lines.append(stripped)
    return '\n'.join(clean_lines)


def build_vector_store():
    """
    Read all 3 knowledge layers -> split into chunks
    -> store in Chroma database with layer metadata.
    """
    print("Building v3 multi-layer vector store...")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=150,
        chunk_overlap=0,
        separators=["\n", ". ", ", "]
    )
    embeddings = get_embeddings()

    all_chunks = []

    for layer_name, file_path in DATASET_FILES.items():
        if not os.path.exists(file_path):
            print(f"  WARNING: {file_path} not found, skipping {layer_name} layer")
            continue

        print(f"  Loading {layer_name} layer from {os.path.basename(file_path)}...")
        clean_text = _load_and_clean(file_path)

        from langchain_core.documents import Document
        doc = Document(page_content=clean_text, metadata={"layer": layer_name})
        chunks = splitter.split_documents([doc])

        # Ensure each chunk carries the layer metadata
        for chunk in chunks:
            chunk.metadata["layer"] = layer_name

        print(f"    Created {len(chunks)} chunks for {layer_name}")
        all_chunks.extend(chunks)

    print(f"\nTotal chunks across all layers: {len(all_chunks)}")

    # Show sample chunks per layer
    for layer_name in DATASET_FILES:
        samples = [c for c in all_chunks if c.metadata.get("layer") == layer_name][:2]
        for s in samples:
            print(f"  [{layer_name}] {s.page_content[:80]}...")

    # Store in Chroma
    print("\nStoring in Chroma database...")
    vector_store = Chroma.from_documents(
        documents=all_chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )
    print("Chroma database saved!\n")
    return vector_store


def load_vector_store():
    """
    Load Chroma database from disk.
    Build fresh if doesn't exist.
    """
    embeddings = get_embeddings()

    if os.path.exists(CHROMA_PATH):
        print("Loading Chroma database...")
        vector_store = Chroma(
            persist_directory=CHROMA_PATH,
            embedding_function=embeddings
        )
        print("Chroma loaded!")
    else:
        print("Building new Chroma database...")
        vector_store = build_vector_store()

    return vector_store


def search_philosophy(query: str, top_k: int = 3) -> list:
    """
    Search most relevant philosophy for a question.
    Backward compat — searches all layers.
    """
    vector_store = load_vector_store()
    results = vector_store.similarity_search(query, k=top_k)
    return [doc.page_content for doc in results]


def search_by_layer(query: str, layer: str = None, top_k: int = 3) -> list:
    """
    Search with optional layer filtering.
    layer: "philosophical", "scientific", "experiential", or None (all)
    Returns list of dicts: {"content": str, "layer": str}
    """
    vector_store = load_vector_store()

    if layer:
        results = vector_store.similarity_search(
            query, k=top_k,
            filter={"layer": layer}
        )
    else:
        results = vector_store.similarity_search(query, k=top_k)

    return [
        {"content": doc.page_content, "layer": doc.metadata.get("layer", "philosophical")}
        for doc in results
    ]
