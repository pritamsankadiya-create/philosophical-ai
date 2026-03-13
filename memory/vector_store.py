# ============================================================
# memory/vector_store.py
# ChromaDB with built-in ONNX embeddings (no Ollama needed)
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
DATASET_PATH = os.path.join(_BASE_DIR, "dataset", "philosophy.txt")


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


def build_vector_store():
    """
    Read philosophy.txt -> split into chunks
    -> store in Chroma database.

    Key fix: chunk_size=150
    Each chunk = roughly ONE quote/sentence
    """
    print("Loading philosophy dataset...")

    # Step 1: Load text file
    loader = TextLoader(DATASET_PATH)
    documents = loader.load()

    # Step 2: Filter out comment lines
    clean_text = []
    for doc in documents:
        lines = doc.page_content.split('\n')
        clean_lines = [
            line for line in lines
            if line.strip()
            and not line.startswith('#')
            and not line.startswith('\u2500')
        ]
        doc.page_content = '\n'.join(clean_lines)
        clean_text.append(doc)

    print(f"Cleaned {len(clean_text)} documents!")

    # Step 3: Split into small chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=150,
        chunk_overlap=0,
        separators=["\n", ". ", ", "]
    )
    chunks = splitter.split_documents(clean_text)
    print(f"Created {len(chunks)} chunks!")

    # Step 4: Show sample chunks
    print("\nSample chunks:")
    for i, chunk in enumerate(chunks[:3]):
        print(f"  Chunk {i+1}: {chunk.page_content[:80]}...")

    # Step 5: Store in Chroma
    print("\nStoring in Chroma database...")
    embeddings = get_embeddings()

    vector_store = Chroma.from_documents(
        documents=chunks,
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
    Uses SEMANTIC SEARCH — understands meaning!
    """
    vector_store = load_vector_store()
    results = vector_store.similarity_search(query, k=top_k)
    return [doc.page_content for doc in results]
