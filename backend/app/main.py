import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(ROOT_DIR, ".env"))

print("--- DIET ENGINE STARTUP ---", flush=True)
from .database import engine, Base
from . import models, models_recommendations
from .llm_config import get_llm_diagnostics
from .routers import auth, profile, recommendations, ai, chat, tracking

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
frontend_urls_raw = os.getenv("FRONTEND_URL", "")
frontend_urls = [url.strip() for url in frontend_urls_raw.split(",") if url.strip()]
if frontend_urls:
    origins.extend(frontend_urls)
    logger.info(f"CORS: Added production origins: {frontend_urls}")
    print(f"DIAGNOSTIC: FRONTEND_URL found: {frontend_urls}", flush=True)
else:
    logger.warning("CORS: No FRONTEND_URL found in environment variables.")
    print("DIAGNOSTIC: No FRONTEND_URL found.", flush=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
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
app.include_router(tracking.router)

@app.get("/")
def read_root():
    return {
        "status": "healthy",
        "service": "Diet Engine Backend",
        "version": "1.0.0",
        "environment": os.getenv("ENV", "development"),
        "cors_frontends_configured": frontend_urls,
    }

@app.get("/diagnostics")
def diagnostics():
    """
    Returns simple diagnostic information useful for verifying CORS and env.
    """
    return {
        "environment": os.getenv("ENV", "development"),
        "frontend_url_env": frontend_urls,
        "cors_origins": origins,
        "cors_origin_regex": r"https://.*\.vercel\.app",
    }

@app.get("/diagnostics/llm")
def llm_diagnostics():
    return get_llm_diagnostics()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
