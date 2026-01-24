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
    
    def _get_embeddings(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for a list of texts using OpenAI.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            print(f"❌ Error generating embeddings: {e}")
            raise
    
    def add_documentation(self, documents: list[str], metadatas: list[dict] = None):
        """
        Add API documentation to the vector database.
        
        Args:
            documents: List of documentation strings to add
            metadatas: Optional list of metadata dictionaries for each document
        """
        if not documents:
            return
        
        # Generate embeddings for documents
        embeddings = self._get_embeddings(documents)
        
        # Generate IDs for documents
        existing_count = self.collection.count()
        ids = [f"doc_{existing_count + i}" for i in range(len(documents))]
        
        # Default metadata if not provided
        if metadatas is None:
            metadatas = [{"source": "api_docs", "type": "documentation"} for _ in documents]
        
        # Add to collection
        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"✅ Added {len(documents)} documents to ChromaDB")
    
    def reset_collection(self):
        """
        Reset the collection (delete all documents).
        Use with caution!
        """
        self.client.delete_collection(name="api_documentation")
        self.collection = self.client.get_or_create_collection(
            name="api_documentation",
            metadata={"description": "Rise Jobs API documentation and usage guidelines"}
        )
        print("🔄 Collection reset successfully")
