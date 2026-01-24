"""
RAG Service for storing and retrieving API documentation using ChromaDB.
This service helps agents make evidence-backed decisions when calling external APIs.
"""
import chromadb
from chromadb.config import Settings
from openai import OpenAI
import os

class RAGService:
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize ChromaDB client and collection.
        
        Args:
            persist_directory: Directory to persist the Chroma database
        """
        self.persist_directory = persist_directory
        
        # Initialize ChromaDB persistent client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection for API documentation
        self.collection = self.client.get_or_create_collection(
            name="api_documentation",
            metadata={"description": "Rise Jobs API documentation and usage guidelines"}
        )
        
        # Initialize OpenAI client for embeddings
        api_key = os.getenv("OPEN_API_KEY")
        if not api_key:
            raise ValueError("OPEN_API_KEY environment variable is not set")
        self.openai_client = OpenAI(api_key=api_key)
        
        # Embedding model to use
        self.embedding_model = "text-embedding-3-small"
        
        print(f"✅ RAG Service initialized")
        print(f"   Database location: {persist_directory}")
        print(f"   Collection: {self.collection.name}")
        print(f"   Documents in collection: {self.collection.count()}")
