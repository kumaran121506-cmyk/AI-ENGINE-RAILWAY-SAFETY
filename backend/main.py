"""
Main entry point for AI-Based Autonomous Railway Safety System Backend with Database connection.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

from app.api.routes import api_router
from app.api.websocket import ws_router
from app.database.session import init_db, SessionLocal
from app.database.repository import DatabaseRepository
from app.config import HOST, PORT

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("railway_safety_backend")

app = FastAPI(
    title="AI-Based Autonomous Railway Safety System Backend",
    description="Real-Time Train Tracking, Signal Aspect Verification, Physics Collision Prediction, and Automatic Emergency Braking (AEB) Control Engine with SQLite Persistence.",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(ws_router)

@app.on_event("startup")
def on_startup():
    logger.info("Initializing Database tables...")
    init_db()
    db = SessionLocal()
    try:
        repo = DatabaseRepository()
        repo.seed_initial_data_if_empty(db)
        logger.info("Database initialized & seeded successfully.")
    finally:
        db.close()

@app.get("/")
async def root():
    return {
        "system": "AI-Based Autonomous Railway Safety System",
        "database": "SQLite Relational Database (Connected)",
        "status": "ONLINE",
        "layer_architecture": [
            "1. Sensing Layer (GPS/GNSS, RFID Balise, Camera Aspect)",
            "2. Communication Layer (V2V, V2I Telemetry Bus, WebSockets)",
            "3. AI Processing Layer (Signal Verification & Kinematic Collision Prediction)",
            "4. Control & Actuation Layer (Automatic Emergency Braking Controller)"
        ],
        "endpoints": {
            "telemetry_ingest": "/api/v1/telemetry",
            "signal_aspect_ingest": "/api/v1/signals",
            "active_trains": "/api/v1/trains",
            "audit_logs": "/api/v1/audits",
            "network_data": "/api/v1/data/network",
            "fleet_data": "/api/v1/data/fleet",
            "live_websocket": "/ws/live-monitoring"
        }
    }

if __name__ == "__main__":
    logger.info(f"Starting Railway Safety System Backend Server on {HOST}:{PORT}")
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
