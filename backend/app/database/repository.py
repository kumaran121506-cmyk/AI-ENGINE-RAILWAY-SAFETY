"""
Database Repository Layer: CRUD operations for Track Corridors, Signals, Fleet, Telemetry, and Audit Logs.
"""

import json
import os
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.database.models import Corridor, TrackSegment, SignalNode, TrainFleet, TrainState, AuditLog
from app.config import DATA_DIR

class DatabaseRepository:
    def seed_initial_data_if_empty(self, db: Session):
        """
        Populates database tables from JSON datasets on initial startup if empty.
        """
        if db.query(Corridor).first() is None:
            track_file = os.path.join(DATA_DIR, "real_track_network.json")
            if os.path.exists(track_file):
                with open(track_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for c_data in data.get("corridors", []):
                        corridor = Corridor(
                            id=c_data["corridor_id"],
                            name=c_data["name"],
                            total_length_km=c_data["total_length_km"],
                            max_speed_kmh=c_data["max_speed_kmh"]
                        )
                        db.add(corridor)
                        for seg_data in c_data.get("segments", []):
                            start_coords = seg_data.get("start_coords", {})
                            end_coords = seg_data.get("end_coords", {})
                            segment = TrackSegment(
                                id=seg_data["segment_id"],
                                corridor_id=c_data["corridor_id"],
                                start_km=seg_data["start_km"],
                                end_km=seg_data["end_km"],
                                start_lat=start_coords.get("lat"),
                                start_lon=start_coords.get("lon"),
                                end_lat=end_coords.get("lat"),
                                end_lon=end_coords.get("lon"),
                                gradient_percent=seg_data.get("gradient_percent", 0.0),
                                speed_limit_kmh=seg_data.get("speed_limit_kmh", 160.0),
                                tracks_count=seg_data.get("tracks", 2)
                            )
                            db.add(segment)

                            for sig in seg_data.get("signals", []):
                                loc = sig.get("location_coords", {})
                                signal = SignalNode(
                                    id=sig["signal_id"],
                                    segment_id=seg_data["segment_id"],
                                    km_marker=sig["km_marker"],
                                    lat=loc.get("lat"),
                                    lon=loc.get("lon"),
                                    digital_state=sig.get("interlocking_digital_state", "PROCEED"),
                                    camera_visual_aspect=sig.get("camera_visual_aspect", "PROCEED")
                                )
                                db.add(signal)

        if db.query(TrainFleet).first() is None:
            fleet_file = os.path.join(DATA_DIR, "train_fleet_data.json")
            if os.path.exists(fleet_file):
                with open(fleet_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for trn in data.get("fleet", []):
                        fleet_item = TrainFleet(
                            train_id=trn["train_id"],
                            name=trn["name"],
                            type=trn["type"],
                            mass_tonnes=trn["total_mass_tonnes"],
                            length_meters=trn["length_meters"],
                            max_speed_kmh=trn["max_service_speed_kmh"],
                            max_accel_ms2=trn.get("max_traction_accel_ms2", 0.7),
                            service_decel_ms2=trn.get("service_decel_ms2", 1.0),
                            emergency_decel_ms2=trn.get("emergency_decel_ms2", 1.4),
                            brake_response_sec=trn.get("brake_response_time_sec", 0.25)
                        )
                        db.add(fleet_item)

        db.commit()

    def update_train_state(self, db: Session, telemetry_data: Dict[str, Any]) -> TrainState:
        train_id = telemetry_data["train_id"]
        state = db.query(TrainState).filter(TrainState.train_id == train_id).first()
        if not state:
            state = TrainState(train_id=train_id)
            db.add(state)

        state.corridor_id = telemetry_data.get("corridor_id", "COR-01")
        state.track_segment_id = telemetry_data["track_segment_id"]
        state.position_km = telemetry_data["position_km"]
        state.speed_kmh = telemetry_data["speed_kmh"]
        state.acceleration_ms2 = telemetry_data.get("acceleration_ms2", 0.0)
        state.heading_deg = telemetry_data.get("heading_deg", 0.0)
        state.last_balise_id = telemetry_data.get("last_balise_id")
        state.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(state)
        return state

    def get_all_active_trains(self, db: Session) -> List[TrainState]:
        return db.query(TrainState).all()

    def update_signal_state(self, db: Session, signal_data: Dict[str, Any]) -> SignalNode:
        sig_id = signal_data["signal_id"]
        node = db.query(SignalNode).filter(SignalNode.id == sig_id).first()
        if not node:
            node = SignalNode(
                id=sig_id,
                segment_id=signal_data["track_segment_id"],
                km_marker=signal_data["km_marker"]
            )
            db.add(node)

        node.digital_state = signal_data["digital_state"]
        node.camera_visual_aspect = signal_data["visual_aspect"]
        node.confidence_score = signal_data.get("confidence", 0.98)

        db.commit()
        db.refresh(node)
        return node

    def get_signal_node(self, db: Session, signal_id: str) -> Optional[SignalNode]:
        return db.query(SignalNode).filter(SignalNode.id == signal_id).first()

    def log_audit_event(
        self,
        db: Session,
        event_type: str,
        train_id: str,
        risk_level: str,
        details: str,
        payload: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        raw_str = json.dumps(payload, default=str) if payload else None
        audit = AuditLog(
            timestamp=datetime.now(timezone.utc),
            event_type=event_type,
            train_id=train_id,
            risk_level=risk_level,
            details=details,
            raw_payload=raw_str
        )
        db.add(audit)
        db.commit()
        db.refresh(audit)
        return audit

    def get_audit_logs(
        self,
        db: Session,
        limit: int = 50,
        train_id: Optional[str] = None,
        risk_level: Optional[str] = None
    ) -> List[AuditLog]:
        query = db.query(AuditLog)
        if train_id:
            query = query.filter(AuditLog.train_id == train_id)
        if risk_level:
            query = query.filter(AuditLog.risk_level == risk_level)
        return query.order_by(AuditLog.id.desc()).limit(limit).all()
