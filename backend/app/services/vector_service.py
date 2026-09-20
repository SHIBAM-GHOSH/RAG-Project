import uuid
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
from backend.app.core.config import settings

class VectorStoreService:
    """Service to handle local embedding generation and Pinecone Vector DB operations."""

    def __init__(self):
        # 1. Load local Sentence Transformer model for generating 384-dim embeddings
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
        
        # 2. Initialize Pinecone client with API key from settings
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index_name = settings.PINECONE_INDEX_NAME
        
        # 3. Create Pinecone index if it doesn't exist yet
        existing_indexes = [idx.name for idx in self.pc.list_indexes()]
        if self.index_name not in existing_indexes:
            self.pc.create_index(
                name=self.index_name,
                dimension=384,  # all-MiniLM-L6-v2 vector dimension
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
            
        # 4. Connect to index
        self.index = self.pc.Index(self.index_name)

    def generate_embedding(self, text: str) -> List[float]:
        """Convert a text string into a 384-dimensional vector float list."""
        embedding = self.embedding_model.encode(text)
        return embedding.tolist()

    def upsert_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        """Embed text chunks and store them in Pinecone with metadata tags."""
        if not chunks:
            return 0

        vectors_to_upsert = []
        for chunk in chunks:
            text_content = chunk["text"]
            metadata = chunk["metadata"]
            # Save raw text inside metadata so we can read it back during query
            metadata["text"] = text_content
            
            # Generate 384-dim vector
            vector_values = self.generate_embedding(text_content)
            chunk_id = str(uuid.uuid4())
            
            vectors_to_upsert.append((chunk_id, vector_values, metadata))

        # Batch upsert into Pinecone
        self.index.upsert(vectors=vectors_to_upsert)
        return len(vectors_to_upsert)

    def query_project_chunks(self, query: str, project_id: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Perform vector search filtered strictly by project_id."""
        query_vector = self.generate_embedding(query)
        
        # Metadata filter guarantees project isolation
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
