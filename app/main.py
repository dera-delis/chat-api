from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, rooms, messages, presence
from app.websocket import chat
from app.config import settings

app = FastAPI(
    title="Real-Time Chat API",
    description="Production-ready real-time chat API with WebSockets, Redis, and PostgreSQL",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(rooms.router)
app.include_router(messages.router)
app.include_router(presence.router)

# WebSocket endpoint
@app.websocket("/ws/chat/{room_id}")
async def websocket_endpoint(websocket, room_id: int):
    """WebSocket endpoint for real-time chat"""
    from app.database import SessionLocal
    
    # Extract token from query parameters
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008, reason="Missing token")
        return
    
    db = SessionLocal()
    try:
        await chat.websocket_chat_endpoint(websocket, room_id, token, db)
    finally:
        db.close()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Real-Time Chat API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

