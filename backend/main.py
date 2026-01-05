"""
AI-Powered Customer Support System
FastAPI Backend with Pinecone RAG and n8n Integration
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import httpx
import os
from datetime import datetime
import uuid
from contextlib import asynccontextmanager

from rag_system import RAGSystem
from config import settings


# Initialize RAG system on startup
rag_system: Optional[RAGSystem] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize RAG system on startup"""
    global rag_system
    rag_system = RAGSystem()
    await rag_system.initialize()
    yield
    # Cleanup if needed


app = FastAPI(
    title="AI Support Assistant",
    description="Intelligent customer support with Pinecone RAG and escalation",
    version="2.0.0",
    lifespan=lifespan
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== Pydantic Models ==============

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = datetime.now()


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_email: Optional[str] = None
    category: Optional[str] = None  # Optional category filter


class ChatResponse(BaseModel):
    response: str
    session_id: str
    sources: List[str] = []
    needs_escalation: bool = False
    confidence_score: float = 0.0


class EscalationRequest(BaseModel):
    session_id: str
    user_email: str
    user_name: Optional[str] = None
    conversation_summary: str
    original_query: str


class EscalationResponse(BaseModel):
    success: bool
    message: str
    ticket_id: Optional[str] = None


class KnowledgeItem(BaseModel):
    id: Optional[str] = None
    title: str
    content: str
    category: Optional[str] = "general"
    product: Optional[str] = "general"


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    category: Optional[str] = None


# ============== In-Memory Session Store ==============
sessions: dict = {}


def get_or_create_session(session_id: Optional[str]) -> tuple[str, List[ChatMessage]]:
    """Get existing session or create new one"""
    if session_id and session_id in sessions:
        return session_id, sessions[session_id]
    
    new_id = str(uuid.uuid4())
    sessions[new_id] = []
    return new_id, sessions[new_id]


# ============== Core Chat Endpoint ==============

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint with RAG-powered responses"""
    session_id, history = get_or_create_session(request.session_id)
    
    # Add user message to history
    user_msg = ChatMessage(role="user", content=request.message)
    history.append(user_msg)
    
    # Get RAG response
    rag_response = await rag_system.get_response(
        query=request.message,
        chat_history=history[:-1],
        filter_category=request.category
    )
    
    # Determine if escalation is needed
    needs_escalation = (
        rag_response["confidence_score"] < 0.5 or
        any(phrase in request.message.lower() for phrase in [
            "talk to human", "speak to agent", "real person",
            "support team", "escalate", "not helpful", "still need help",
            "manager", "supervisor", "complaint"
        ])
    )
    
    # Build response
    response_text = rag_response["response"]
    
    if needs_escalation and not request.user_email:
        response_text += "\n\n---\n📧 **I'd be happy to connect you with our support team!** Please provide your email address, and I'll have someone reach out to you shortly."
    
    # Add assistant message to history
    assistant_msg = ChatMessage(role="assistant", content=response_text)
    history.append(assistant_msg)
    
    return ChatResponse(
        response=response_text,
        session_id=session_id,
        sources=rag_response.get("sources", []),
        needs_escalation=needs_escalation,
        confidence_score=rag_response["confidence_score"]
    )


# ============== Escalation Endpoint ==============

@app.post("/api/escalate", response_model=EscalationResponse)
async def escalate_to_support(request: EscalationRequest):
    """Trigger n8n webhook for email escalation"""
    try:
        # Generate ticket ID
        ticket_id = f"TKT-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        # Prepare payload for n8n webhook
        payload = {
            "ticket_id": ticket_id,
            "session_id": request.session_id,
            "user_email": request.user_email,
            "user_name": request.user_name or "Customer",
            "conversation_summary": request.conversation_summary,
            "original_query": request.original_query,
            "timestamp": datetime.now().isoformat(),
            "priority": "normal"
        }
        
        # Send to n8n webhook
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.N8N_WEBHOOK_URL,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
        
        return EscalationResponse(
            success=True,
            message="Your request has been sent to our support team. You'll receive an email shortly.",
            ticket_id=ticket_id
        )
        
    except httpx.HTTPError as e:
        print(f"n8n webhook error: {e}")
        raise HTTPException(
            status_code=503,
            detail="Unable to reach support system. Please try again later."
        )


# ============== Knowledge Management ==============

@app.post("/api/knowledge/add")
async def add_knowledge(item: KnowledgeItem):
    """Add new knowledge to RAG system"""
    try:
        doc_id = item.id or str(uuid.uuid4())
        await rag_system.add_document(
            doc_id=doc_id,
            title=item.title,
            content=item.content,
            metadata={
                "category": item.category,
                "product": item.product
            }
        )
        return {"status": "success", "message": f"Added: {item.title}", "id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/knowledge/search")
async def search_knowledge(request: SearchRequest):
    """Search the knowledge base"""
    try:
        filter_dict = None
        if request.category:
            filter_dict = {"category": {"$eq": request.category}}
            
        results = await rag_system.search_similar(
            query=request.query,
            top_k=request.top_k,
            filter_dict=filter_dict
        )
        return {"results": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/knowledge/clear")
async def clear_knowledge():
    """Clear all documents from knowledge base (use carefully!)"""
    try:
        await rag_system.delete_all_documents()
        return {"status": "success", "message": "All documents deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============== Health & Info ==============

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "rag_initialized": rag_system is not None,
        "version": "2.0.0 - Pinecone Edition"
    }


@app.get("/api/stats")
async def get_stats():
    """Get system statistics"""
    doc_count = await rag_system.get_document_count() if rag_system else 0
    return {
        "active_sessions": len(sessions),
        "knowledge_items": doc_count,
        "vector_db": "Pinecone",
        "llm": "Groq - Llama 3.3 70B"
    }


@app.get("/api/categories")
async def get_categories():
    """Get available knowledge categories"""
    return {
        "categories": [
            "shipping",
            "returns",
            "payment",
            "account",
            "orders",
            "products",
            "promo",
            "tech_support",
            "warranty",
            "subscription",
            "laptop",
            "phone",
            "headphones",
            "smartwatch",
            "tv",
            "gaming",
            "smart_home",
            "fitness",
            "camera",
            "tablet"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
