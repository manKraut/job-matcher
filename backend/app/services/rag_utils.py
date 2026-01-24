"""
Utility functions for agents to retrieve and use RAG documentation.
"""
import os
from typing import List, Optional

# Lazy initialization of RAG service
_rag_service = None

def get_rag_service():
    """Get or initialize RAG service (lazy loading)."""
    global _rag_service
    if _rag_service is None:
        try:
            # Only initialize if API key is available
            if os.getenv("OPEN_API_KEY"):
                from app.services.rag_service import RAGService
                _rag_service = RAGService(persist_directory="./chroma_db")
            else:
                return None
        except Exception as e:
            # Graceful fallback if RAG service can't be initialized
            return None
    return _rag_service

def get_api_documentation_for_agent(query: str, n_results: int = 3) -> str:
    """
    Retrieve and format API documentation for use in agent prompts.
    
    Args:
        query: Search query to find relevant documentation
        n_results: Number of documentation chunks to retrieve
        
    Returns:
        Formatted string with API documentation, or empty string if unavailable
    """
    rag_service = get_rag_service()
    if rag_service is None:
        return ""
    
    try:
        docs = rag_service.retrieve_relevant_docs(query, n_results=n_results)
        if docs:
            return rag_service.format_docs_for_prompt(docs)
    except Exception as e:
        # Graceful fallback - continue without RAG docs
        return ""
    
    return ""
