import os
import sys
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("--- DIET ENGINE STARTUP ---", flush=True)
from .database import engine, Base
from . import models, models_recommendations
from .routers import auth, profile, recommendations, ai, chat

# Load environment variables for production
load_dotenv()

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Diet Engine API",
    description="Production-ready API for the Diet Engine Platform"
)

from .seeder import seed_database
from .database import SessionLocal

@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

# CORS Configuration
# In production, set FRONTEND_URL environment variable (e.g., https://your-diet-engine.vercel.app)
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5173",
    "http://172.20.10.3:5174",
    "http://192.168.1.34:5173", # Previous Laptop IP
    "http://192.168.1.40:5173",
]
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    origins.append(frontend_url)
    logger.info(f"CORS: Added production origin: {frontend_url}")
    print(f"DIAGNOSTIC: FRONTEND_URL found: {frontend_url}", flush=True)
else:
    logger.warning("CORS: No FRONTEND_URL found in environment variables.")
    print("DIAGNOSTIC: No FRONTEND_URL found.", flush=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(recommendations.router)
app.include_router(ai.router)
app.include_router(chat.router)

@app.get("/")
def read_root():
    return {
        "status": "healthy",
        "service": "Diet Engine Backend",
        "version": "1.0.0",
        "environment": os.getenv("ENV", "development")
    }

@app.get("/diagnostics")
def diagnostics():
    """
    Returns simple diagnostic information useful for verifying CORS and env.
    """
    return {
        "environment": os.getenv("ENV", "development"),
        "frontend_url_env": frontend_url,
        "cors_origins": origins,
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
