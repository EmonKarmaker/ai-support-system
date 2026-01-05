"""
Data Loader Script
Loads e-commerce customer support dataset into Pinecone
Run this once to populate your knowledge base
"""

import pandas as pd
import asyncio
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_system import RAGSystem
from config import settings
from tqdm import tqdm


async def load_csv_to_pinecone(csv_path: str):
    """Load CSV dataset and vectorize into Pinecone"""
    
    print("=" * 60)
    print("🚀 E-Commerce Support Dataset Loader")
    print("=" * 60)
    
    # Initialize RAG system
    rag_system = RAGSystem()
    await rag_system.initialize()
    
    # Load CSV
    print(f"\n📂 Loading dataset from: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"📊 Found {len(df)} records")
    print(f"📋 Categories: {df['category'].unique().tolist()}")
    
    # Prepare documents
    documents = []
    for _, row in df.iterrows():
        documents.append({
            "id": f"doc_{row['id']}",
            "title": row['question'],
            "content": row['answer'],
            "category": row['category'],
            "product": row['product']
        })
    
    # Upload to Pinecone
    print(f"\n🔄 Uploading {len(documents)} documents to Pinecone...")
    print("   (This may take a few minutes for embedding generation)")
    
    await rag_system.add_documents_batch(documents)
    
    # Verify upload
    print("\n✅ Upload complete!")
    count = await rag_system.get_document_count()
    print(f"📈 Total vectors in Pinecone: {count}")
    
    # Test search
    print("\n🧪 Testing search...")
    test_results = await rag_system.search_similar("How do I return an item?", top_k=3)
    print(f"   Query: 'How do I return an item?'")
    print(f"   Found {len(test_results)} results:")
    for i, result in enumerate(test_results, 1):
        print(f"   {i}. [{result['score']:.3f}] {result['title'][:50]}...")
    
    print("\n" + "=" * 60)
    print("✨ Dataset loaded successfully!")
    print("=" * 60)


async def main():
    # Path to CSV file
    csv_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data",
        "ecommerce_support_dataset.csv"
    )
    
    # Check if file exists
    if not os.path.exists(csv_path):
        print(f"❌ Error: CSV file not found at {csv_path}")
        print("   Make sure ecommerce_support_dataset.csv is in the /data folder")
        return
    
    # Check if API keys are set
    if not settings.PINECONE_API_KEY:
        print("❌ Error: PINECONE_API_KEY not set in .env file")
        return
    
    if not settings.GROQ_API_KEY:
        print("❌ Error: GROQ_API_KEY not set in .env file")
        return
    
    await load_csv_to_pinecone(csv_path)


if __name__ == "__main__":
    asyncio.run(main())
