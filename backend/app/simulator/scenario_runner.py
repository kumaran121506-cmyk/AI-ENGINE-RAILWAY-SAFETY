"""
Scenario Simulation Runner: Runs real-time scenario tests demonstrating train tracking,
signal mismatch detection, collision prediction, and automatic emergency braking actuation.
"""

import time
import json
from typing import Dict, Any, List
from app.models.schemas import TrainTelemetryInput, SignalAspectInput
from app.services.sensing_service import SensingService
from app.services.signal_verification import SignalVerificationEngine
from app.services.collision_prediction import CollisionPredictionEngine
from app.services.control_actuation import ControlActuationService
from app.services.audit_logger import AuditLogger
from app.database.session import SessionLocal, init_db
from app.database.repository import DatabaseRepository

class ScenarioRunner:
    def __init__(self):
        init_db()
        self.db = SessionLocal()
        self.repo = DatabaseRepository()
        self.repo.seed_initial_data_if_empty(self.db)
        self.sensing = SensingService()
        self.signal_verifier = SignalVerificationEngine()
        self.collision_engine = CollisionPredictionEngine()
        self.actuation = ControlActuationService()
        self.audit_logger = AuditLogger()

    def run_signal_mismatch_scenario(self) -> List[Dict[str, Any]]:
        """
        Scenario 1: Train approaching SIG-101-B where Digital Interlocking = STOP,
        but visual camera feed misidentifies it as PROCEED.
        Expectation: Signal Verification flags CRITICAL mismatch and triggers AEB.
        """
        results = []

        # Register signal aspect with mismatch
        sig_input = SignalAspectInput(
            signal_id="SIG-101-B",
            track_segment_id="SEG-101",
            km_marker=18.5,
            interlocking_digital_state="STOP",
            camera_visual_aspect="PROCEED",
            confidence_score=0.96
        )
        self.sensing.process_signal_aspect(sig_input, db=self.db)
        sig_result = self.signal_verifier.verify_signal(sig_input)

        # Telemetry: Train approaching signal at 145 km/h
        telemetry = TrainTelemetryInput(
            train_id="TRN-EXPRESS-101",
            track_segment_id="SEG-101",
            position_km=17.8,
            speed_kmh=145.0,
            heading_deg=140.0
        )
        train_state = self.sensing.process_telemetry(telemetry, db=self.db)

        # Calculate Collision Risk & Stopping Distance
        collision_risk = self.collision_engine.evaluate_train_risk(
            current_train=train_state,
            other_trains=[],
            signal_state=self.sensing.get_signal_state("SIG-101-B", db=self.db)
        )

        # Control Actuation
        braking_cmd = self.actuation.issue_braking_command(
            train_id="TRN-EXPRESS-101",
            current_speed_kmh=145.0,
            collision_risk=collision_risk,
            signal_verification=sig_result
        )

        if braking_cmd:
            self.repo.log_audit_event(
                db=self.db,
                event_type="SIGNAL_INTERVENTION",
                train_id="TRN-EXPRESS-101",
                risk_level=braking_cmd.risk_level,
                details=braking_cmd.reason
            )

        results.append({
            "step": 1,
            "scenario_name": "Signal Mismatch / Red Light Protection",
            "train_id": "TRN-EXPRESS-101",
            "speed_kmh": 145.0,
            "position_km": 17.8,
            "signal_verification": sig_result.dict(),
            "collision_risk": collision_risk.dict(),
            "braking_command": braking_cmd.dict() if braking_cmd else None
        })

        return results

    def run_head_on_collision_scenario(self) -> List[Dict[str, Any]]:
        """
        Scenario 2: Two trains on same track segment SEG-101 moving toward each other.
        TRN-EXPRESS-101 at 18.0 km moving forward (140 km/h).
        TRN-FREIGHT-302 at 19.5 km moving backward (80 km/h).
        Gap = 1,500m.
        Expectation: Collision prediction engine calculates safe stopping clearance > 1,500m, flags CRITICAL,
        and triggers automatic emergency braking on both trains.
        """
        results = []

        t1_telemetry = TrainTelemetryInput(
            train_id="TRN-EXPRESS-101",
            track_segment_id="SEG-101",
            position_km=18.0,
            speed_kmh=140.0,
            heading_deg=140.0
        )
        t2_telemetry = TrainTelemetryInput(
            train_id="TRN-FREIGHT-302",
            track_segment_id="SEG-101",
            position_km=18.8,
            speed_kmh=80.0,
            heading_deg=320.0
        )

        t1_state = self.sensing.process_telemetry(t1_telemetry, db=self.db)
        t2_state = self.sensing.process_telemetry(t2_telemetry, db=self.db)

        all_trains = list(self.sensing.get_all_active_trains(db=self.db).values())

        # Evaluate T1
        t1_risk = self.collision_engine.evaluate_train_risk(t1_state, all_trains)
        t1_cmd = self.actuation.issue_braking_command("TRN-EXPRESS-101", 140.0, t1_risk)
        if t1_cmd:
            self.repo.log_audit_event(db=self.db, event_type="COLLISION_INTERVENTION", train_id="TRN-EXPRESS-101", risk_level=t1_cmd.risk_level, details=t1_cmd.reason)

        # Evaluate T2
        t2_risk = self.collision_engine.evaluate_train_risk(t2_state, all_trains)
        t2_cmd = self.actuation.issue_braking_command("TRN-FREIGHT-302", 80.0, t2_risk)
        if t2_cmd:
            self.repo.log_audit_event(db=self.db, event_type="COLLISION_INTERVENTION", train_id="TRN-FREIGHT-302", risk_level=t2_cmd.risk_level, details=t2_cmd.reason)

        results.append({
            "scenario_name": "Imminent Head-On Collision Prevention",
            "train_1": {
                "id": "TRN-EXPRESS-101",
                "risk": t1_risk.dict(),
                "braking_command": t1_cmd.dict() if t1_cmd else None
            },
            "train_2": {
                "id": "TRN-FREIGHT-302",
                "risk": t2_risk.dict(),
                "braking_command": t2_cmd.dict() if t2_cmd else None
            }
        })

        return results
