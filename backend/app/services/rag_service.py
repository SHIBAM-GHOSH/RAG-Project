from typing import List, Dict, Any
from groq import Groq
from backend.app.core.config import settings
from backend.app.services.vector_service import vector_service

class RAGService:
    """Service to handle RAG prompt formatting and Groq LLM inference calls."""

    def __init__(self, model_name: str = "groq/compound"):
        self.model_name = model_name
        self.client = None
        if settings.GROQ_API_KEY:
            try:
                self.client = Groq(api_key=settings.GROQ_API_KEY)
            except Exception as e:
                print(f"Warning: Could not initialize Groq client: {e}")

    def build_prompt(self, query: str, context_chunks: List[Dict[str, Any]]) -> str:
        """Format retrieved context chunks and query into a grounded system prompt."""
        if not context_chunks:
            return "NO_CONTEXT_FOUND"

        context_text = ""
        for i, chunk in enumerate(context_chunks, start=1):
            filename = chunk.get("filename", "Document")
            page = chunk.get("page", 1)   
            text = chunk.get("text", "")[:1000]
            context_text += f"\n--- Chunk [{i}] (File: {filename}, Page: {page}) ---\n{text}\n"

        prompt = f"""You are a helpful study assistant. Answer the user's question STRICTLY based on the provided context below.
        If the context does not contain enough information to answer the question, respond with: "I cannot find relevant information in your uploaded project documents to answer this question."

        CONTEXT:
        {context_text}

        USER QUESTION:
        {query}

        ANSWER:"""
        return prompt

    def answer_question(self, query: str, project_id: str, top_k: int = 3) -> Dict[str, Any]:
        """Perform full RAG: Retrieve Pinecone chunks -> Call Groq LLM -> Return answer + citations."""
        chunks = vector_service.query_project_chunks(query=query, project_id=project_id, top_k=top_k)
        
        prompt = self.build_prompt(query, chunks)
        if prompt == "NO_CONTEXT_FOUND":
            return {
                "answer": "I cannot find any relevant documents in this project to answer your question. Please upload a study PDF first!",
                "sources": []
            }

        if not self.client:
            return {
                "answer": "Groq API client is not configured. Please check your GROQ_API_KEY setting.",
                "sources": []
            }
            
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are an expert AI study assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        
        answer_text = response.choices[0].message.content
        
        sources = []
        for chunk in chunks:
            sources.append({
                "filename": chunk.get("filename", ""),
                "page": chunk.get("page", 1),
                "text_snippet": chunk.get("text", "")[:100]
            })
            
        return {
            "answer": answer_text,
            "sources": sources
        }

# Instantiate a global RAG service object
rag_service = RAGService()
