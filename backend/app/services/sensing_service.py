"""
Sensing Layer Service: Manages GPS/GNSS telemetry ingestion, RFID Balise position corrections,
and track-side camera aspect feeds backed by SQLite Database.
"""

import math
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.models.schemas import TrainTelemetryInput, SignalAspectInput
from app.database.repository import DatabaseRepository

class SensingService:
    def __init__(self):
        # In-memory backup cache
        self.active_trains: Dict[str, Dict[str, Any]] = {}
        self.signal_states: Dict[str, Dict[str, Any]] = {}
        self.repo = DatabaseRepository()

    def process_telemetry(self, telemetry: TrainTelemetryInput, db: Optional[Session] = None) -> Dict[str, Any]:
        """
        Ingests train telemetry. Updates both in-memory cache and SQL Database.
        """
        corrected_position_km = telemetry.position_km
        if telemetry.last_balise_id:
            corrected_position_km = round(telemetry.position_km, 4)

        train_state = {
            "train_id": telemetry.train_id,
            "corridor_id": telemetry.corridor_id,
            "track_segment_id": telemetry.track_segment_id,
            "position_km": corrected_position_km,
            "speed_kmh": telemetry.speed_kmh,
            "speed_ms": telemetry.speed_kmh / 3.6,
            "acceleration_ms2": telemetry.acceleration_ms2,
            "heading_deg": telemetry.heading_deg,
            "last_balise_id": telemetry.last_balise_id,
            "coords": telemetry.coords.dict() if telemetry.coords else None
        }

        self.active_trains[telemetry.train_id] = train_state

        if db:
            self.repo.update_train_state(db, train_state)

        return train_state

    def process_signal_aspect(self, signal_input: SignalAspectInput, db: Optional[Session] = None) -> Dict[str, Any]:
        """
        Registers updated signal state from digital interlocking and onboard camera feed.
        """
        signal_state = {
            "signal_id": signal_input.signal_id,
            "track_segment_id": signal_input.track_segment_id,
            "km_marker": signal_input.km_marker,
            "digital_state": signal_input.interlocking_digital_state,
            "visual_aspect": signal_input.camera_visual_aspect,
            "confidence": signal_input.confidence_score
        }
        self.signal_states[signal_input.signal_id] = signal_state

        if db:
            self.repo.update_signal_state(db, signal_state)

        return signal_state

    def get_all_active_trains(self, db: Optional[Session] = None) -> Dict[str, Dict[str, Any]]:
        if db:
            db_trains = self.repo.get_all_active_trains(db)
            result = {}
            for t in db_trains:
                result[t.train_id] = {
                    "train_id": t.train_id,
                    "corridor_id": t.corridor_id,
                    "track_segment_id": t.track_segment_id,
                    "position_km": t.position_km,
                    "speed_kmh": t.speed_kmh,
                    "speed_ms": t.speed_kmh / 3.6,
                    "acceleration_ms2": t.acceleration_ms2,
                    "heading_deg": t.heading_deg,
                    "last_balise_id": t.last_balise_id
                }
            return result
        return self.active_trains

    def get_signal_state(self, signal_id: str, db: Optional[Session] = None) -> Optional[Dict[str, Any]]:
        if db:
            node = self.repo.get_signal_node(db, signal_id)
            if node:
                return {
                    "signal_id": node.id,
                    "track_segment_id": node.segment_id,
                    "km_marker": node.km_marker,
                    "digital_state": node.digital_state,
                    "visual_aspect": node.camera_visual_aspect,
                    "confidence": node.confidence_score
                }
        return self.signal_states.get(signal_id)
