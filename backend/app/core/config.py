import os
from dotenv import load_dotenv

# Fix OpenBLAS thread memory conflict on Windows
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"


# Load key-value pairs from the .env file into environment variables
load_dotenv()

class Settings:
    """Central configuration class for application settings & API keys"""
    
    # Groq API key for LLM inference calls
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # Pinecone cloud credentials for vector database
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "study-rag-index")
    
    # HuggingFace embedding model name
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")

# Instantiate a single global settings object to be imported across the app
settings = Settings()
