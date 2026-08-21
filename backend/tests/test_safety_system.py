"""
Automated PyTest Suite for Railway Safety System Backend.
"""

import pytest
from app.services.sensing_service import SensingService
from app.services.signal_verification import SignalVerificationEngine
from app.services.collision_prediction import CollisionPredictionEngine
from app.services.control_actuation import ControlActuationService
from app.models.schemas import TrainTelemetryInput, SignalAspectInput

def test_stopping_distance_calculation():
    engine = CollisionPredictionEngine()
    # At 140 km/h (38.89 m/s), decel 1.2 m/s2, reaction 0.25s
    # reaction_dist = 38.89 * 0.25 = 9.72m
    # braking_dist = 38.89^2 / (2 * 1.2) = 1512.42 / 2.4 = 630.17m
    # total ~ 639.9m
    d_stop = engine.calculate_stopping_distance(speed_kmh=140.0, decel_ms2=1.2, gradient_percent=0.0)
    assert d_stop > 600.0 and d_stop < 660.0

def test_signal_verification_mismatch():
    verifier = SignalVerificationEngine()
    sig_input = SignalAspectInput(
        signal_id="SIG-01",
        track_segment_id="SEG-101",
        km_marker=10.0,
        interlocking_digital_state="STOP",
        camera_visual_aspect="PROCEED",
        confidence_score=0.95
    )
    result = verifier.verify_signal(sig_input)
    assert result.mismatch_detected is True
    assert result.alert_level == "CRITICAL"

def test_head_on_collision_prediction():
    engine = CollisionPredictionEngine()
    t1 = {
        "train_id": "TRN-1",
        "track_segment_id": "SEG-101",
        "position_km": 10.0,
        "speed_kmh": 140.0,
        "heading_deg": 90.0
    }
    t2 = {
        "train_id": "TRN-2",
        "track_segment_id": "SEG-101",
        "position_km": 11.0,  # 1000 meters away
        "speed_kmh": 120.0,
        "heading_deg": 270.0
    }
    risk = engine.evaluate_train_risk(t1, [t1, t2])
    assert risk.risk_level == "CRITICAL"
    assert risk.action_required == "EMERGENCY_BRAKE"

def test_control_actuation_emergency_braking():
    actuation = ControlActuationService()
    engine = CollisionPredictionEngine()
    t1 = {
        "train_id": "TRN-1",
        "track_segment_id": "SEG-101",
        "position_km": 10.0,
        "speed_kmh": 140.0
    }
    t2 = {
        "train_id": "TRN-2",
        "track_segment_id": "SEG-101",
        "position_km": 10.8,
        "speed_kmh": 100.0,
        "heading_deg": 270.0
    }
    risk = engine.evaluate_train_risk(t1, [t1, t2])
    cmd = actuation.issue_braking_command("TRN-1", 140.0, risk)
    assert cmd is not None
    assert cmd.emergency_brake_engaged is True
    assert cmd.braking_intensity_percent == 100.0
