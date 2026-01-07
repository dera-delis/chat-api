from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.routers import auth, rooms, messages, presence
from app.websocket import chat
from app.config import settings
import traceback

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
    import traceback
    
    print(f"[WebSocket] Connection attempt to room {room_id}")
    
    # Accept WebSocket connection first (required before sending messages)
    try:
        await websocket.accept()
        print(f"[WebSocket] Connection accepted for room {room_id}")
    except Exception as e:
        print(f"[WebSocket] Failed to accept connection: {e}")
        print(f"[WebSocket] Traceback: {traceback.format_exc()}")
        return
    
    # Extract token from query parameters
    token = websocket.query_params.get("token")
    if not token:
        print(f"[WebSocket] Missing token for room {room_id}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": "Missing authentication token"
            })
            await websocket.close(code=1008, reason="Missing token")
        except:
            pass
        return
    
    print(f"[WebSocket] Token received for room {room_id}")
    
    db = SessionLocal()
    try:
        await chat.websocket_chat_endpoint(websocket, room_id, token, db)
    except Exception as e:
        error_traceback = traceback.format_exc()
        print(f"[WebSocket] Error in chat endpoint: {e}")
        print(f"[WebSocket] Traceback: {error_traceback}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": "Server error",
                "detail": str(e)
            })
            await websocket.close(code=1011, reason=f"Server error: {str(e)}")
        except Exception as close_error:
            print(f"[WebSocket] Failed to send error message: {close_error}")
    finally:
        db.close()
        print(f"[WebSocket] Connection closed for room {room_id}")


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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed messages"""
    errors = exc.errors()
    print(f"Validation error: {errors}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": errors,
            "message": "Validation error. Please check your request format."
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler to catch unhandled errors"""
    # Log the full traceback for debugging
    error_traceback = traceback.format_exc()
    print(f"Unhandled exception: {error_traceback}")
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": f"Internal server error: {str(exc)}",
            "type": type(exc).__name__
        }
    )

