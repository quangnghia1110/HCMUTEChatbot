import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL")
TEMPERATURE = float(os.getenv("TEMPERATURE"))
MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS"))
TOP_K = float(os.getenv("TOP_K"))
TOP_P = float(os.getenv("TOP_P"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES"))
BASE_DELAY = int(os.getenv("BASE_DELAY"))
MAX_DOCS = int(os.getenv("MAX_DOCS"))
SEMANTIC_WEIGHT = float(os.getenv("SEMANTIC_WEIGHT"))
KEYWORD_WEIGHT = float(os.getenv("KEYWORD_WEIGHT"))
VECTOR_SEARCH_K = int(os.getenv("VECTOR_SEARCH_K"))
VECTOR_CONTENT_PREVIEW = int(os.getenv("VECTOR_CONTENT_PREVIEW"))
VECTOR_SEARCH_WEIGHT = float(os.getenv("VECTOR_SEARCH_WEIGHT"))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP"))
PDF_SOURCE = os.getenv("PDF_SOURCE") 