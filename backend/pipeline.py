import json
import os
import sys

# Support both direct run and exec()-based run (Colab)
_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.getcwd()
sys.path.insert(0, _dir)

from config import RAW_DATA_FILE, CHUNKS_FILE, DATA_DIR
from crawler import crawl
from extractor import extract_all
from chunker import chunk_documents
from vector_store import build_index


def run_pipeline():
    os.makedirs(DATA_DIR, exist_ok=True)

    print("=== Step 1: Crawling ===")
    pages = crawl()
    if not pages:
        print("[ERROR] No pages crawled. Check network access and BASE_URL.")
        return
    with open(RAW_DATA_FILE, "w") as f:
        json.dump([{"url": p["url"]} for p in pages], f, indent=2)

    print(f"\n=== Step 2: Extracting ({len(pages)} pages) ===")
    docs = extract_all(pages)
    print(f"[Extractor] {len(docs)} docs with content")

    print("\n=== Step 3: Chunking ===")
    chunks = chunk_documents(docs)
    if not chunks:
        print("[ERROR] No chunks created. Check extractor output.")
        return
    with open(CHUNKS_FILE, "w") as f:
        json.dump(chunks, f, indent=2)

    print("\n=== Step 4: Building Vector Index ===")
    build_index(chunks)

    print(f"\n=== Pipeline Complete: {len(pages)} pages, {len(chunks)} chunks ===")


if __name__ == "__main__":
    run_pipeline()
