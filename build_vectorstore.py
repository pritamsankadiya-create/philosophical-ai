"""Pre-build ChromaDB during Docker image build."""

from memory.vector_store import build_vector_store

if __name__ == "__main__":
    build_vector_store()
