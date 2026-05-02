from tagger import classify_tag
from config import CHUNK_SIZE, CHUNK_OVERLAP


def split_words(text, size, overlap):
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i: i + size])
        chunks.append(chunk)
        i += size - overlap
    return chunks


def chunk_documents(docs):
    chunks = []
    chunk_id = 0
    for doc in docs:
        for section in doc["sections"]:
            text = section["text"]
            tag = classify_tag(section["heading"] + " " + text)
            for chunk_text in split_words(text, CHUNK_SIZE, CHUNK_OVERLAP):
                if len(chunk_text.split()) < 20:
                    continue
                chunks.append({
                    "chunk_id": chunk_id,
                    "text": chunk_text,
                    "tag": tag,
                    "url": doc["url"],
                    "section": section["heading"],
                    "title": doc["title"],
                })
                chunk_id += 1
    print(f"[Chunker] Created {len(chunks)} chunks")
    return chunks
