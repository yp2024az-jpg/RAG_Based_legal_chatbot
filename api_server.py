from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
from src.core.chatbot import LegalAdvisorBot
from src.utils import setup_logger

logger = setup_logger(__name__)

app = FastAPI(
    title="Legal Advisor Chatbot API",
    description="RAG-based Legal Advisor Chatbot API using FastAPI",
    version="1.0.0"
)

# Initialize the chatbot lazily
bot = None

def get_bot() -> LegalAdvisorBot:
    global bot
    if bot is None:
        try:
            bot = LegalAdvisorBot()
            logger.info("Bot initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}")
            raise HTTPException(status_code=500, detail=f"Bot initialization failed: {str(e)}")
    return bot

class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class SessionRequest(BaseModel):
    session_id: str

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to the Legal Advisor Chatbot API"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    global bot
    if bot is not None:
        return {"status": "healthy", "bot_initialized": True}
    else:
        return {"status": "unhealthy", "bot_initialized": False}

@app.post("/query")
async def process_query(request: QueryRequest):
    """Process a legal query"""
    try:
        bot_instance = get_bot()
        response = bot_instance.query(request.query, request.session_id)
        return response
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/session/start")
async def start_session(request: SessionRequest):
    """Start a new session"""
    try:
        bot_instance = get_bot()
        bot_instance.start_session(request.session_id)
        return {"message": f"Session {request.session_id} started"}
    except Exception as e:
        logger.error(f"Error starting session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/session/end")
async def end_session(request: SessionRequest):
    """End a session"""
    try:
        bot_instance = get_bot()
        bot_instance.end_session(request.session_id)
        return {"message": f"Session {request.session_id} ended"}
    except Exception as e:
        logger.error(f"Error ending session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/stats")
async def get_stats():
    """Get bot statistics"""
    try:
        bot_instance = get_bot()
        stats = bot_instance.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/reset")
async def reset_bot():
    """Reset the bot"""
    try:
        global bot
        bot = None  # Reset to None so it reinitializes on next use
        return {"message": "Bot reset successfully"}
    except Exception as e:
        logger.error(f"Error resetting bot: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
