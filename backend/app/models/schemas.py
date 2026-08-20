"""
Pydantic schemas for request/response payloads in Railway Safety Backend.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class GPSCoordinates(BaseModel):
    lat: float = Field(..., example=28.6139)
    lon: float = Field(..., example=77.2090)

class TrainTelemetryInput(BaseModel):
    train_id: str = Field(..., example="TRN-EXPRESS-101")
    corridor_id: str = Field(default="COR-01", example="COR-01")
    track_segment_id: str = Field(..., example="SEG-101")
    position_km: float = Field(..., description="Current position along track corridor in km", example=12.5)
    speed_kmh: float = Field(..., description="Current train velocity in km/h", example=140.0)
    acceleration_ms2: float = Field(default=0.0, description="Current acceleration in m/s^2", example=0.0)
    heading_deg: float = Field(default=140.0, description="Direction heading in degrees", example=140.0)
    last_balise_id: Optional[str] = Field(default=None, example="BAL-101-1")
    coords: Optional[GPSCoordinates] = None

class SignalAspectInput(BaseModel):
    signal_id: str = Field(..., example="SIG-101-B")
    track_segment_id: str = Field(..., example="SEG-101")
    km_marker: float = Field(..., example=18.5)
    interlocking_digital_state: str = Field(..., description="STOP | CAUTION | PROCEED", example="STOP")
    camera_visual_aspect: str = Field(..., description="STOP | CAUTION | PROCEED", example="PROCEED")
    confidence_score: float = Field(default=0.98, description="Camera CV model confidence score [0.0 - 1.0]")

class SignalVerificationResult(BaseModel):
    signal_id: str
    is_valid: bool
    digital_state: str
    visual_aspect: str
    mismatch_detected: bool
    alert_level: str
    details: str

class CollisionRiskResult(BaseModel):
    train_id: str
    other_train_id: Optional[str] = None
    distance_gap_meters: Optional[float] = None
    calculated_stopping_distance_meters: float
    risk_level: str  # NORMAL, WARNING, CRITICAL
    action_required: str  # NONE, ADVISORY_SLOW, EMERGENCY_BRAKE
    explanation: str

class BrakingCommand(BaseModel):
    command_id: str
    train_id: str
    timestamp: datetime
    risk_level: str
    emergency_brake_engaged: bool
    braking_intensity_percent: float
    target_speed_kmh: float
    calculated_stopping_distance_m: float
    reason: str

class TelemetryProcessResponse(BaseModel):
    timestamp: datetime
    train_id: str
    current_speed_kmh: float
    position_km: float
    signal_verification: Optional[SignalVerificationResult]
    collision_risk: CollisionRiskResult
    braking_command: Optional[BrakingCommand]
    system_status: str

class TrackSegmentSummary(BaseModel):
    segment_id: str
    start_km: float
    end_km: float
    speed_limit_kmh: float
    gradient_percent: float
    active_train_count: int

class AuditLogItem(BaseModel):
    id: int
    timestamp: str
    event_type: str
    train_id: str
    risk_level: str
    details: str
