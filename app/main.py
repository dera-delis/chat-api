from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, rooms, messages, presence
from app.websocket import chat

app = FastAPI(
    title="Real-Time Chat API",
    description="Production-ready real-time chat API with WebSockets, Redis, and PostgreSQL",
    version="1.0.0"
)

# CORS middleware - must be added FIRST (before other middleware)
# Note: When allow_credentials=True, you cannot use allow_origins=["*"]
# Must specify exact origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers - register more specific routes first to avoid conflicts
app.include_router(auth.router)
app.include_router(messages.router)  # /rooms/{room_id}/messages - more specific, register first
app.include_router(rooms.router)      # /rooms/{room_id} - less specific, register after
app.include_router(presence.router)

@app.websocket("/ws/chat/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: int):
    await chat.websocket_chat_endpoint(websocket, room_id)


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




