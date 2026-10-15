#!/usr/bin/env python3
"""
Initialization script to populate ChromaDB with API documentation.
Run this script once to set up the RAG database, or whenever documentation is updated.

Usage:
    python scripts/init_rag_db.py
    or
    python -m scripts.init_rag_db
"""
import sys
import os
from pathlib import Path

# Add parent directory to path to import app modules
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.rag_service import RAGService
from app.services.api_documentation import ARBEITNOW_API_DOCS

def main():
    """Initialize and populate the RAG database with API documentation."""
    print("🚀 Initializing RAG Database with ChromaDB...")
    print("=" * 60)
    
    # Initialize RAG service
    try:
        rag_service = RAGService(persist_directory="./chroma_db")
        print("✅ RAG service initialized\n")
    except Exception as e:
        print(f"❌ Error initializing RAG service: {e}")
        print("   Make sure OPEN_API_KEY environment variable is set")
        return 1
    
    # Check if database already has documents
    doc_count = rag_service.collection.count()
    if doc_count > 0:
        print(f"⚠️  Database already contains {doc_count} documents")
        response = input("   Do you want to reset and repopulate? (yes/no): ").strip().lower()
        if response in ['yes', 'y']:
            rag_service.reset_collection()
            print("   Database reset\n")
        else:
            print("   Keeping existing documents. Exiting.")
            return 0
    
    # Create metadata for each document
    metadatas = []
    doc_types = [
        "endpoint_info",
        "query_parameters",
        "request_examples",
        "response_structure",
        "best_practices",
        "error_handling",
        "data_transformation",
        "pagination",
        "integration_notes"
    ]
    
    for i, doc in enumerate(ARBEITNOW_API_DOCS):
        metadatas.append({
            "source": "arbeitnow_job_board_api",
            "type": doc_types[i] if i < len(doc_types) else "general",
            "api_name": "Arbeitnow Job Board API",
            "version": "v1"
        })
    
    # Add documentation to database
    print(f"📚 Adding {len(ARBEITNOW_API_DOCS)} documentation chunks to database...")
    print("   This may take a moment as embeddings are generated...\n")
    
    try:
        rag_service.add_documentation(
            documents=ARBEITNOW_API_DOCS,
            metadatas=metadatas
        )
        
        # Display final info
        final_count = rag_service.collection.count()
        print("\n" + "=" * 60)
        print("✅ RAG Database initialized successfully!")
        print(f"   Collection: {rag_service.collection.name}")
        print(f"   Documents: {final_count}")
        print(f"   Location: {rag_service.persist_directory}")
        print("\n💡 You can now use RAG in your agents for evidence-backed API calls!")
        return 0
        
    except Exception as e:
        print(f"\n❌ Error adding documents: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
