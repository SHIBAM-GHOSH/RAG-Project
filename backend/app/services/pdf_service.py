import io
from typing import List, Dict, Any
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

class PDFProcessor:
    """Service to process PDF files, extract text page-by-page, and chunk it into vector-ready segments."""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        # Configure text splitter (paragraphs -> newlines -> words)
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )

    def extract_text_from_pdf(self, file_bytes: bytes, filename: str) -> List[Dict[str, Any]]:
        """Extract text page by page from raw uploaded PDF bytes."""
        reader = PdfReader(io.BytesIO(file_bytes))
        pages_data = []
        
        # Extract text from every page
        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                pages_data.append({
                    "page": page_num,
                    "text": text,
                    "filename": filename
                })
        return pages_data

    def chunk_pdf(self, file_bytes: bytes, filename: str, project_id: str) -> List[Dict[str, Any]]:
        """Extract page text and split into smaller chunks with metadata attached."""
        pages = self.extract_text_from_pdf(file_bytes, filename)
        chunks_with_metadata = []
        
        # Split text on each page and attach metadata tags
        for page_info in pages:
            raw_text = page_info["text"]
            page_chunks = self.splitter.split_text(raw_text)
            
            for chunk_text in page_chunks:
                chunks_with_metadata.append({
                    "text": chunk_text,
                    "metadata": {
                        "project_id": project_id,
                        "filename": filename,
                        "page": page_info["page"]
                    }
                })
                
        return chunks_with_metadata

# Create a global processor instance
pdf_processor = PDFProcessor()
