import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL, VECTOR_STORE_DIR, CHUNKS_FILE

INDEX_FILE = os.path.join(VECTOR_STORE_DIR, "faiss.index")
META_FILE = os.path.join(VECTOR_STORE_DIR, "metadata.json")

_model = None
_index = None
_metadata = None


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def build_index(chunks):
    if not chunks:
        print("[VectorStore] No chunks to index. Aborting.")
        return False
    os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
    model = get_model()
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings.astype("float32"))

    faiss.write_index(index, INDEX_FILE)
    with open(META_FILE, "w") as f:
        json.dump(chunks, f)
    print(f"[VectorStore] Indexed {len(chunks)} chunks")


def load_index():
    global _index, _metadata
    if _index is None:
        _index = faiss.read_index(INDEX_FILE)
        with open(META_FILE) as f:
            _metadata = json.load(f)
    return _index, _metadata


def retrieve(query, top_k=5):
    index, metadata = load_index()
    model = get_model()
    q_emb = model.encode([query], convert_to_numpy=True)
    q_emb = q_emb / np.linalg.norm(q_emb, axis=1, keepdims=True)
    scores, indices = index.search(q_emb.astype("float32"), top_k)
    return [metadata[i] for i in indices[0] if i < len(metadata)]
