"""
REST API Routes for Railway Safety Backend with SQLite Database persistence.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from app.models.schemas import (
    TrainTelemetryInput,
    SignalAspectInput,
    TelemetryProcessResponse,
    SignalVerificationResult,
    CollisionRiskResult,
    BrakingCommand,
    AuditLogItem
)
from app.database.session import get_db
from app.database.repository import DatabaseRepository
from app.services.sensing_service import SensingService
from app.services.signal_verification import SignalVerificationEngine
from app.services.collision_prediction import CollisionPredictionEngine
from app.services.control_actuation import ControlActuationService
from app.services.audit_logger import AuditLogger
from app.services.analytics_service import AnalyticsService
from app.api.websocket import manager

api_router = APIRouter(prefix="/api/v1")

# Singletons & Repo
sensing_service = SensingService()
signal_verifier = SignalVerificationEngine()
collision_engine = CollisionPredictionEngine()
actuation_service = ControlActuationService()
audit_logger = AuditLogger()
analytics_service = AnalyticsService()
repo = DatabaseRepository()


@api_router.post("/telemetry", response_model=TelemetryProcessResponse)
async def process_telemetry(
    telemetry: TrainTelemetryInput,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Core Sensing -> AI Processing -> Control & Actuation loop backed by Database.
    """
    # 1. Sensing Layer (persists state to DB)
    train_state = sensing_service.process_telemetry(telemetry, db=db)

    # 2. Signal Aspect Check
    target_signal_id = f"SIG-101-B" if telemetry.position_km > 15.0 else f"SIG-101-A"
    current_signal_feed = sensing_service.get_signal_state(target_signal_id, db=db)

    signal_result: Optional[SignalVerificationResult] = None
    if current_signal_feed:
        sig_input = SignalAspectInput(
            signal_id=target_signal_id,
            track_segment_id=telemetry.track_segment_id,
            km_marker=current_signal_feed["km_marker"],
            interlocking_digital_state=current_signal_feed["digital_state"],
            camera_visual_aspect=current_signal_feed["visual_aspect"],
            confidence_score=current_signal_feed.get("confidence", 0.98)
        )
        signal_result = signal_verifier.verify_signal(sig_input)

    # 3. AI Collision Prediction Engine
    all_trains = list(sensing_service.get_all_active_trains(db=db).values())
    collision_risk: CollisionRiskResult = collision_engine.evaluate_train_risk(
        current_train=train_state,
        other_trains=all_trains,
        signal_state=current_signal_feed
    )

    # 4. Control & Actuation Layer
    braking_cmd: Optional[BrakingCommand] = actuation_service.issue_braking_command(
        train_id=telemetry.train_id,
        current_speed_kmh=telemetry.speed_kmh,
        collision_risk=collision_risk,
        signal_verification=signal_result
    )

    # 5. Database Audit Log & Broadcast
    if braking_cmd or collision_risk.risk_level != "NORMAL" or (signal_result and signal_result.mismatch_detected):
        risk_lvl = braking_cmd.risk_level if braking_cmd else collision_risk.risk_level
        log_detail = braking_cmd.reason if braking_cmd else collision_risk.explanation
        repo.log_audit_event(
            db=db,
            event_type="SAFETY_INTERVENTION",
            train_id=telemetry.train_id,
            risk_level=risk_lvl,
            details=log_detail,
            payload={
                "telemetry": telemetry.dict(),
                "collision_risk": collision_risk.dict(),
                "braking_command": braking_cmd.dict() if braking_cmd else None
            }
        )

    response_payload = TelemetryProcessResponse(
        timestamp=datetime.now(timezone.utc),
        train_id=telemetry.train_id,
        current_speed_kmh=telemetry.speed_kmh,
        position_km=telemetry.position_km,
        signal_verification=signal_result,
        collision_risk=collision_risk,
        braking_command=braking_cmd,
        system_status="ACTIVE_MONITORING"
    )

    background_tasks.add_task(manager.broadcast, response_payload.dict())

    return response_payload


@api_router.post("/signals")
async def update_signal_state(signal_input: SignalAspectInput, db: Session = Depends(get_db)):
    """
    Ingests and registers trackside signal aspect feeds directly into the Database.
    """
    state = sensing_service.process_signal_aspect(signal_input, db=db)
    verification = signal_verifier.verify_signal(signal_input)
    return {"status": "REGISTERED_IN_DB", "signal_state": state, "verification": verification}


@api_router.get("/trains")
async def get_active_trains(db: Session = Depends(get_db)):
    """
    Returns real-time status of all active trains queried from Database.
    """
    return sensing_service.get_all_active_trains(db=db)


@api_router.get("/audits", response_model=List[AuditLogItem])
async def get_audit_logs(limit: int = 50, train_id: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Fetches compliance audit log entries directly from SQL Database.
    """
    db_logs = repo.get_audit_logs(db=db, limit=limit, train_id=train_id)
    results = []
    for log in db_logs:
        results.append(AuditLogItem(
            id=log.id,
            timestamp=log.timestamp.isoformat() if isinstance(log.timestamp, datetime) else str(log.timestamp),
            event_type=log.event_type,
            train_id=log.train_id,
            risk_level=log.risk_level,
            details=log.details
        ))
    return results


@api_router.get("/data/network")
async def get_real_network_data():
    return analytics_service.get_network_overview()


@api_router.get("/data/fleet")
async def get_real_fleet_data():
    return analytics_service.get_fleet_specifications()
