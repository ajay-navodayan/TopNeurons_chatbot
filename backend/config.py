import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "https://www.topneurons.org")
MAX_PAGES = int(os.getenv("MAX_PAGES", 100))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 250))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 50))
TOP_K = int(os.getenv("TOP_K", 5))
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Use __file__ if available (normal run), else fall back to cwd (exec/Colab)
_BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.getcwd()
DATA_DIR = os.path.join(_BASE_DIR, "..", "data")
VECTOR_STORE_DIR = os.path.join(_BASE_DIR, "..", "vector_store")
RAW_DATA_FILE = os.path.join(DATA_DIR, "raw_pages.json")
CHUNKS_FILE = os.path.join(DATA_DIR, "chunks.json")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
