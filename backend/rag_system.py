"""
RAG System with Pinecone Vector Database + Sentence Transformers + Groq LLM
All Free Tier Compatible
"""

import os
from typing import List, Dict, Optional
import httpx
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
import json

from config import settings


class RAGSystem:
    def __init__(self):
        self.pc: Optional[Pinecone] = None
        self.index = None
        self.embedding_model = None
        self.groq_model = "llama-3.3-70b-versatile"  # Free tier
        self.embedding_dimension = 384  # all-MiniLM-L6-v2 dimension
        
    async def initialize(self):
        """Initialize Pinecone and embedding model"""
        print("🔄 Initializing RAG System...")
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        
        # Check if index exists, if not create it
        existing_indexes = [idx.name for idx in self.pc.list_indexes()]
        
        if settings.PINECONE_INDEX_NAME not in existing_indexes:
            print(f"📦 Creating Pinecone index: {settings.PINECONE_INDEX_NAME}")
            self.pc.create_index(
                name=settings.PINECONE_INDEX_NAME,
                dimension=self.embedding_dimension,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"  # Free tier region
                )
            )
        
        # Connect to index
        self.index = self.pc.Index(settings.PINECONE_INDEX_NAME)
        
        # Load embedding model locally (free, no API needed)
        print("🧠 Loading embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        print("✅ RAG System initialized")
        
    def get_embedding(self, text: str) -> List[float]:
        """Get embeddings using local sentence-transformers model"""
        embedding = self.embedding_model.encode(text)
        return embedding.tolist()
    
    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts at once (faster)"""
        embeddings = self.embedding_model.encode(texts)
        return embeddings.tolist()
    
    async def add_document(
        self,
        doc_id: str,
        title: str,
        content: str,
        metadata: Optional[Dict] = None
    ):
        """Add single document to Pinecone"""
        embedding = self.get_embedding(f"{title} {content}")
        
        # Prepare metadata
        meta = {
            "title": title,
            "content": content[:1000],  # Pinecone metadata limit
            **(metadata or {})
        }
        
        # Upsert to Pinecone
        self.index.upsert(vectors=[{
            "id": doc_id,
            "values": embedding,
            "metadata": meta
        }])
        
    async def add_documents_batch(self, documents: List[Dict]):
        """Add multiple documents at once (faster)"""
        # Prepare texts for batch embedding
        texts = [f"{doc['title']} {doc['content']}" for doc in documents]
        embeddings = self.get_embeddings_batch(texts)
        
        # Prepare vectors for upsert
        vectors = []
        for i, doc in enumerate(documents):
            vectors.append({
                "id": doc["id"],
                "values": embeddings[i],
                "metadata": {
                    "title": doc["title"],
                    "content": doc["content"][:1000],
                    "category": doc.get("category", "general"),
                    "product": doc.get("product", "general")
                }
            })
        
        # Upsert in batches of 100 (Pinecone limit)
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            self.index.upsert(vectors=batch)
            print(f"📤 Uploaded batch {i//batch_size + 1}/{(len(vectors)-1)//batch_size + 1}")
    
    async def search_similar(
        self,
        query: str,
        top_k: int = 5,
        filter_dict: Optional[Dict] = None
    ) -> List[Dict]:
        """Search for similar documents in Pinecone"""
        query_embedding = self.get_embedding(query)
        
        # Query Pinecone
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            filter=filter_dict
        )
        
        # Format results
        documents = []
        for match in results.matches:
            documents.append({
                "id": match.id,
                "score": match.score,
                "title": match.metadata.get("title", ""),
                "content": match.metadata.get("content", ""),
                "category": match.metadata.get("category", ""),
                "product": match.metadata.get("product", "")
            })
        
        return documents
    
    async def get_response(
        self,
        query: str,
        chat_history: List = None,
        filter_category: str = None
    ) -> Dict:
        """Generate RAG response using Groq"""
        
        # 1. Build filter if category specified
        filter_dict = None
        if filter_category:
            filter_dict = {"category": {"$eq": filter_category}}
        
        # 2. Search for relevant context
        relevant_docs = await self.search_similar(query, top_k=5, filter_dict=filter_dict)
        
        # 3. Build context from retrieved documents
        context_parts = []
        for doc in relevant_docs:
            context_parts.append(f"**{doc['title']}** (Category: {doc['category']})\n{doc['content']}")
        
        context = "\n\n---\n\n".join(context_parts) if context_parts else "No specific information found in knowledge base."
        
        # 4. Build chat history context
        history_text = ""
        if chat_history:
            history_text = "\n".join([
                f"{msg.role.upper()}: {msg.content}"
                for msg in chat_history[-5:]  # Last 5 messages
            ])
        
        # 5. Create prompt
        system_prompt = """You are a helpful, friendly customer support assistant for TechStore - an electronics and e-commerce company.

Your job is to:
1. Answer questions based on the provided knowledge base context
2. Be concise but thorough
3. If you're not sure about something, say so honestly
4. If the user's question can't be answered from the context, acknowledge this and offer to connect them with human support

IMPORTANT GUIDELINES:
- Always be polite and professional
- Use the context provided to give accurate answers
- If context doesn't contain the answer, say "I don't have specific information about that, but I can connect you with our support team"
- For product recommendations, consider the user's needs
- Keep responses focused and helpful
- If user seems frustrated, acknowledge their feelings and offer escalation"""

        user_prompt = f"""## Knowledge Base Context:
{context}

## Recent Conversation:
{history_text}

## Customer Question:
{query}

Please provide a helpful response based on the context above."""

        # 6. Call Groq API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.groq_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1024
                },
                timeout=60.0
            )
            response.raise_for_status()
            result = response.json()
        
        assistant_response = result["choices"][0]["message"]["content"]
        
        # 7. Calculate confidence score
        confidence = self._calculate_confidence(relevant_docs)
        
        return {
            "response": assistant_response,
            "sources": [doc["title"] for doc in relevant_docs],
            "confidence_score": confidence,
            "context_used": len(relevant_docs) > 0
        }
    
    def _calculate_confidence(self, docs: List[Dict]) -> float:
        """Calculate confidence score based on retrieved documents"""
        if not docs:
            return 0.3
        
        # Use similarity scores
        scores = [doc.get("score", 0.5) for doc in docs]
        avg_score = sum(scores) / len(scores)
        
        # Boost if multiple relevant docs found
        doc_factor = min(len(docs) / 3, 1.0)
        
        return min(avg_score * doc_factor * 1.2, 1.0)
    
    async def get_document_count(self) -> int:
        """Get total document count from Pinecone"""
        try:
            stats = self.index.describe_index_stats()
            return stats.total_vector_count
        except:
            return 0
    
    async def delete_all_documents(self):
        """Delete all documents from index (use carefully!)"""
        self.index.delete(delete_all=True)
        print("🗑️ All documents deleted from index")
