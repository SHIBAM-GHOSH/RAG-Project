import uuid
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
from backend.app.core.config import settings

class VectorStoreService:
    """Service to handle local embedding generation and Pinecone Vector DB operations."""

    def __init__(self):
        self.embedding_model = None
        self.pc = None
        self.index = None
        self.index_name = settings.PINECONE_INDEX_NAME

        # Initialize Pinecone only if an API key is provided
        if settings.PINECONE_API_KEY:
            try:
                self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
                existing_indexes = [idx.name for idx in self.pc.list_indexes()]
                if self.index_name not in existing_indexes:
                    self.pc.create_index(
                        name=self.index_name,
                        dimension=384,  # all-MiniLM-L6-v2 vector dimension
                        metric="cosine",
                        spec=ServerlessSpec(cloud="aws", region="us-east-1")
                    )
                self.index = self.pc.Index(self.index_name)
            except Exception as e:
                print(f"Warning: Could not initialize Pinecone index: {e}")

    def generate_embedding(self, text: str) -> List[float]:
        """Lazy-load SentenceTransformer and convert text string into vector float list."""
        if self.embedding_model is None:
            self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
        embedding = self.embedding_model.encode(text)
        return embedding.tolist()

    def upsert_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        """Embed text chunks and store them in Pinecone with metadata tags."""
        if not chunks or not self.index:
            return 0

        vectors_to_upsert = []
        for chunk in chunks:
            text_content = chunk["text"]
            metadata = chunk["metadata"]
            metadata["text"] = text_content
            
            vector_values = self.generate_embedding(text_content)
            chunk_id = str(uuid.uuid4())
            
            vectors_to_upsert.append((chunk_id, vector_values, metadata))

        self.index.upsert(vectors=vectors_to_upsert)
        return len(vectors_to_upsert)

    def query_project_chunks(self, query: str, project_id: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Perform vector search filtered strictly by project_id."""
        if not self.index:
            return []

        query_vector = self.generate_embedding(query)
        
        response = self.index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True,
            filter={"project_id": {"$eq": project_id}}
        )
        
        results = []
        for match in response.get("matches", []):
            results.append({
                "score": match.get("score"),
                "text": match.get("metadata", {}).get("text", ""),
                "filename": match.get("metadata", {}).get("filename", ""),
                "page": match.get("metadata", {}).get("page", 1)
            })
            
        return results

# Create a global vector service instance
vector_service = VectorStoreService()
