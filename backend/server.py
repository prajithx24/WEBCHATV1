from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Dict, Set
import json
import os
from dotenv import load_dotenv

# Import models and database
from models.user import User, Base as UserBase
from models.message import Message, Base as MessageBase
from services.database import engine, get_db
from services.auth import decode_access_token

# Import API routers
from api.auth import router as auth_router
from api.users import router as users_router

load_dotenv()

# Create database tables
UserBase.metadata.create_all(bind=engine)
MessageBase.metadata.create_all(bind=engine)

# Initialize FastAPI
app = FastAPI(
    title="Secure E2EE Chat API",
    description="End-to-end encrypted chat application with zero-knowledge architecture",
    version="1.0.0"
)

# CORS Configuration for Vercel deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth_router)
app.include_router(users_router)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        # Map user_id -> WebSocket connection
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        print(f"[WebSocket] User {user_id} connected. Total: {len(self.active_connections)}")
    
    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            print(f"[WebSocket] User {user_id} disconnected. Total: {len(self.active_connections)}")
    
    async def send_to_user(self, user_id: str, message: dict):
        """Send message to specific user"""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(message)
                return True
            except Exception as e:
                print(f"[WebSocket] Error sending to {user_id}: {e}")
                self.disconnect(user_id)
                return False
        return False

manager = ConnectionManager()

@app.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str, db: Session = Depends(get_db)):
    """
    WebSocket endpoint for real-time encrypted message relay.
    Authenticates via JWT token and relays ciphertext between users.
    Server never sees plaintext messages (zero-knowledge architecture).
    """
    user_id = None
    
    try:
        # Authenticate user via token
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        # Verify user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        # Connect user
        await manager.connect(user_id, websocket)
        
        # Send connection success message
        await websocket.send_json({
            "type": "connected",
            "user_id": user_id,
            "message": "Connected to secure chat"
        })
        
        # Listen for messages
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Validate message structure
            if "to_user_id" not in message_data or "ciphertext" not in message_data:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid message format. Required: to_user_id, ciphertext"
                })
                continue
            
            to_user_id = message_data["to_user_id"]
            ciphertext = message_data["ciphertext"]
            
            # Store encrypted message in database (optional for message history)
            new_message = Message(
                from_user_id=user_id,
                to_user_id=to_user_id,
                ciphertext=ciphertext
            )
            db.add(new_message)
            db.commit()
            
            # Relay encrypted message to recipient
            relay_message = {
                "type": "message",
                "from_user_id": user_id,
                "message_id": new_message.id,
                "ciphertext": ciphertext,
                "timestamp": new_message.created_at.isoformat()
            }
            
            # Try to send to recipient
            sent = await manager.send_to_user(to_user_id, relay_message)
            
            # Send delivery confirmation to sender
            await websocket.send_json({
                "type": "sent",
                "message_id": new_message.id,
                "delivered": sent,
                "timestamp": new_message.created_at.isoformat()
            })
    
    except WebSocketDisconnect:
        print(f"[WebSocket] User {user_id} disconnected normally")
    except Exception as e:
        print(f"[WebSocket] Error: {e}")
    finally:
        if user_id:
            manager.disconnect(user_id)

@app.get("/")
async def root():
    return {
        "message": "Secure E2EE Chat API",
        "status": "online",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("BACKEND_PORT", 8001))
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)
