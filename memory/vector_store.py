# ============================================================
# 📁 memory/vector_store.py
# ✅ Fixed chunk size — one quote per chunk!
# ============================================================

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader

CHROMA_PATH = "memory/chroma_db"
DATASET_PATH = "dataset/philosophy.txt"


def get_embeddings():
    """
    Load embedding model.
    nomic-embed-text is fast and accurate!
    """
    return OllamaEmbeddings(model="nomic-embed-text")


def build_vector_store():
    """
    Read philosophy.txt → split into chunks
    → store in Chroma database.

    Key fix: chunk_size=150
    Each chunk = roughly ONE quote/sentence
    So search finds EXACT relevant quote! ✅
    """
    print("📄 Loading philosophy dataset...")

    # Step 1: Load text file
    loader = TextLoader(DATASET_PATH)
    documents = loader.load()

    # Step 2: Filter out comment lines (# ─── lines)
    # These were polluting our chunks before!
    clean_text = []
    for doc in documents:
        lines = doc.page_content.split('\n')
        clean_lines = [
            line for line in lines
            if line.strip()           # remove empty lines
            and not line.startswith('#')  # remove comments
            and not line.startswith('─')  # remove dividers
        ]
        doc.page_content = '\n'.join(clean_lines)
        clean_text.append(doc)

    print(f"✅ Cleaned {len(clean_text)} documents!")

    # Step 3: Split into small chunks
    # chunk_size=150 = roughly one sentence/quote
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=150,    # ✅ one quote per chunk
        chunk_overlap=0,   # ✅ no overlap needed
        separators=[
            "\n",   # split by line first
            ". ",   # then by sentence
            ", ",   # then by comma
        ]
    )
    chunks = splitter.split_documents(clean_text)
    print(f"✅ Created {len(chunks)} chunks!")

    # Step 4: Show sample chunks (for debugging)
    print("\n📋 Sample chunks:")
    for i, chunk in enumerate(chunks[:3]):
        print(f"  Chunk {i+1}: {chunk.page_content[:80]}...")

    # Step 5: Store in Chroma
    print("\n🗄️ Storing in Chroma database...")
    embeddings = get_embeddings()

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )
    print("💾 Chroma database saved!\n")
    return vector_store


def load_vector_store():
    """
    Load Chroma database from disk.
    Build fresh if doesn't exist.
    """
    embeddings = get_embeddings()

    if os.path.exists(CHROMA_PATH):
        print("📂 Loading Chroma database...")
        vector_store = Chroma(
            persist_directory=CHROMA_PATH,
            embedding_function=embeddings
        )
        print("✅ Chroma loaded!")
    else:
        print("🔨 Building new Chroma database...")
        vector_store = build_vector_store()

    return vector_store


def search_philosophy(query: str, top_k: int = 3) -> list:
    """
    Search most relevant philosophy for a question.

    Uses SEMANTIC SEARCH — understands meaning!
    Example:
        Query: "consciousness"
        Finds: Shankaracharya + Patanjali quotes ✅

        Query: "love"
        Finds: Osho + Krishna + Tagore quotes ✅

        Query: "success"
        Finds: Kalam + Chanakya + Vivekananda quotes ✅

    Args:
        query  : search question
        top_k  : how many quotes to fetch (3 = best balance)

    Returns:
        List of relevant philosophy strings
    """
    vector_store = load_vector_store()
    results = vector_store.similarity_search(query, k=top_k)
    return [doc.page_content for doc in results]