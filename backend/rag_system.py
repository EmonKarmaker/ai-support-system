"""
RAG System with Pinecone + HuggingFace API + Groq LLM
Optimized for low memory (Render Free Tier)
"""

import os
from typing import List, Dict, Optional
import httpx
from pinecone import Pinecone, ServerlessSpec

from config import settings


class RAGSystem:
    def __init__(self):
        self.pc: Optional[Pinecone] = None
        self.index = None
        self.groq_model = "llama-3.3-70b-versatile"
        self.embedding_dimension = 384
        self.hf_model = "sentence-transformers/all-MiniLM-L6-v2"
        
    async def initialize(self):
        """Initialize Pinecone connection"""
        print("🔄 Initializing RAG System...")
        
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        
        existing_indexes = [idx.name for idx in self.pc.list_indexes()]
        
        if settings.PINECONE_INDEX_NAME not in existing_indexes:
            print(f"📦 Creating Pinecone index: {settings.PINECONE_INDEX_NAME}")
            self.pc.create_index(
                name=settings.PINECONE_INDEX_NAME,
                dimension=self.embedding_dimension,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
        
        self.index = self.pc.Index(settings.PINECONE_INDEX_NAME)
        print("✅ RAG System initialized")
        
    async def get_embedding(self, text: str) -> List[float]:
        """Get embeddings from HuggingFace API (free, no local memory)"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api-inference.huggingface.co/pipeline/feature-extraction/{self.hf_model}",
                headers={"Authorization": f"Bearer {settings.HF_TOKEN}"},
                json={"inputs": text, "options": {"wait_for_model": True}},
                timeout=60.0
            )
            response.raise_for_status()
            embedding = response.json()
            
            if isinstance(embedding[0], list):
                import numpy as np
                embedding = np.mean(embedding, axis=1).tolist()[0]
            
            return embedding
    
    async def add_document(
        self,
        doc_id: str,
        title: str,
        content: str,
        metadata: Optional[Dict] = None
    ):
        """Add single document to Pinecone"""
        embedding = await self.get_embedding(f"{title} {content}")
        
        meta = {
            "title": title,
            "content": content[:1000],
            **(metadata or {})
        }
        
        self.index.upsert(vectors=[{
            "id": doc_id,
            "values": embedding,
            "metadata": meta
        }])
        
    async def add_documents_batch(self, documents: List[Dict]):
        """Add multiple documents"""
        vectors = []
        for doc in documents:
            text = f"{doc['title']} {doc['content']}"
            embedding = await self.get_embedding(text)
            vectors.append({
                "id": doc["id"],
                "values": embedding,
                "metadata": {
                    "title": doc["title"],
                    "content": doc["content"][:1000],
                    "category": doc.get("category", "general"),
                    "product": doc.get("product", "general")
                }
            })
            print(f"📤 Embedded: {doc['title'][:50]}...")
        
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            self.index.upsert(vectors=batch)
    
    async def search_similar(
        self,
        query: str,
        top_k: int = 5,
        filter_dict: Optional[Dict] = None
    ) -> List[Dict]:
        """Search for similar documents"""
        query_embedding = await self.get_embedding(query)
        
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            filter=filter_dict
        )
        
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
        
        filter_dict = None
        if filter_category:
            filter_dict = {"category": {"$eq": filter_category}}
        
        relevant_docs = await self.search_similar(query, top_k=5, filter_dict=filter_dict)
        
        context_parts = []
        for doc in relevant_docs:
            context_parts.append(f"**{doc['title']}**\n{doc['content']}")
        
        context = "\n\n---\n\n".join(context_parts) if context_parts else "No specific information found."
        
        history_text = ""
        if chat_history:
            history_text = "\n".join([
                f"{msg.role.upper()}: {msg.content}"
                for msg in chat_history[-5:]
            ])
        
        system_prompt = """You are a helpful customer support assistant for TechStore.
Answer based on the provided context. Be concise and helpful.
If you can't answer from context, offer to connect with human support."""

        user_prompt = f"""Context:
{context}

Conversation:
{history_text}

Question: {query}

Provide a helpful response."""

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
        
        confidence = self._calculate_confidence(relevant_docs)
        
        return {
            "response": assistant_response,
            "sources": [doc["title"] for doc in relevant_docs],
            "confidence_score": confidence,
            "context_used": len(relevant_docs) > 0
        }
    
    def _calculate_confidence(self, docs: List[Dict]) -> float:
        if not docs:
            return 0.3
        scores = [doc.get("score", 0.5) for doc in docs]
        avg_score = sum(scores) / len(scores)
        doc_factor = min(len(docs) / 3, 1.0)
        return min(avg_score * doc_factor * 1.2, 1.0)
    
    async def get_document_count(self) -> int:
        try:
            stats = self.index.describe_index_stats()
            return stats.total_vector_count
        except:
            return 0
    
    async def delete_all_documents(self):
        self.index.delete(delete_all=True)