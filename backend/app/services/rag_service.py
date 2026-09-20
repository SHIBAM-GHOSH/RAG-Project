from typing import List, Dict, Any
from groq import Groq
from backend.app.core.config import settings
from backend.app.services.vector_service import vector_service

class RAGService:
    """Service to handle RAG prompt formatting and Groq LLM inference calls."""

    def __init__(self, model_name: str = "groq/compound"):
        # Initialize official Groq client with API key from settings
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model_name = model_name


    def build_prompt(self, query: str, context_chunks: List[Dict[str, Any]]) -> str:
        """Format retrieved context chunks and query into a grounded system prompt."""
        if not context_chunks:
            return "NO_CONTEXT_FOUND"

        # Combine retrieved context snippets with page citations
        context_text = ""
        for i, chunk in enumerate(context_chunks, start=1):
            filename = chunk.get("filename", "Document")
            page = chunk.get("page", 1)   
            text = chunk.get("text", "")[:1000]
            context_text += f"\n--- Chunk [{i}] (File: {filename}, Page: {page}) ---\n{text}\n"

        # Construct strict RAG prompt to prevent hallucinations
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
        # 1. Fetch top relevant text chunks from Pinecone filtered by project_id
        chunks = vector_service.query_project_chunks(query=query, project_id=project_id, top_k=top_k)
        
        # 2. Build grounded RAG prompt
        prompt = self.build_prompt(query, chunks)
        if prompt == "NO_CONTEXT_FOUND":
            return {
                "answer": "I cannot find any relevant documents in this project to answer your question. Please upload a study PDF first!",
                "sources": []
            }
            
        # 3. Call official Groq LLM API
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are an expert AI study assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2  # Low temperature for factual, grounded answers
        )
        
        answer_text = response.choices[0].message.content
        
        # 4. Format page citations
        sources = []
        for chunk in chunks:
            sources.append({
                "filename": chunk.get("filename", ""),
                "page": chunk.get("page", 1),
                "text_snippet": chunk.get("text", "")[:100]  # Short preview snippet
            })
            
        return {
            "answer": answer_text,
            "sources": sources
        }

# Instantiate a global RAG service object
rag_service = RAGService()


