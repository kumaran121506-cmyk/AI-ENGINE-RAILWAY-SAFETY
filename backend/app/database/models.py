"""
SQLAlchemy Database ORM Models for Railway Safety System.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.session import Base

class Corridor(Base):
    __tablename__ = "corridors"

    id = Column(String, primary_key=True)  # e.g., COR-01
    name = Column(String, nullable=False)
    total_length_km = Column(Float, nullable=False)
    max_speed_kmh = Column(Float, nullable=False)

    segments = relationship("TrackSegment", back_populates="corridor", cascade="all, delete-orphan")

class TrackSegment(Base):
    __tablename__ = "track_segments"

    id = Column(String, primary_key=True)  # e.g., SEG-101
    corridor_id = Column(String, ForeignKey("corridors.id"), nullable=False)
    start_km = Column(Float, nullable=False)
    end_km = Column(Float, nullable=False)
    start_lat = Column(Float, nullable=True)
    start_lon = Column(Float, nullable=True)
    end_lat = Column(Float, nullable=True)
    end_lon = Column(Float, nullable=True)
    gradient_percent = Column(Float, default=0.0)
    speed_limit_kmh = Column(Float, nullable=False)
    tracks_count = Column(Integer, default=2)

    corridor = relationship("Corridor", back_populates="segments")
    signals = relationship("SignalNode", back_populates="segment", cascade="all, delete-orphan")

class SignalNode(Base):
    __tablename__ = "signal_nodes"

    id = Column(String, primary_key=True)  # e.g., SIG-101-A
    segment_id = Column(String, ForeignKey("track_segments.id"), nullable=False)
    km_marker = Column(Float, nullable=False)
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)
    digital_state = Column(String, default="PROCEED")
    camera_visual_aspect = Column(String, default="PROCEED")
    confidence_score = Column(Float, default=0.98)

    segment = relationship("TrackSegment", back_populates="signals")

class TrainFleet(Base):
    __tablename__ = "train_fleet"

    train_id = Column(String, primary_key=True)  # e.g., TRN-EXPRESS-101
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    mass_tonnes = Column(Float, nullable=False)
    length_meters = Column(Float, nullable=False)
    max_speed_kmh = Column(Float, nullable=False)
    max_accel_ms2 = Column(Float, default=0.7)
    service_decel_ms2 = Column(Float, default=1.0)
    emergency_decel_ms2 = Column(Float, default=1.4)
    brake_response_sec = Column(Float, default=0.25)

class TrainState(Base):
    __tablename__ = "train_states"

    train_id = Column(String, primary_key=True)
    corridor_id = Column(String, default="COR-01")
    track_segment_id = Column(String, nullable=False)
    position_km = Column(Float, nullable=False)
    speed_kmh = Column(Float, nullable=False)
    acceleration_ms2 = Column(Float, default=0.0)
    heading_deg = Column(Float, default=0.0)
    last_balise_id = Column(String, nullable=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    event_type = Column(String, nullable=False)
    train_id = Column(String, nullable=False)
    risk_level = Column(String, nullable=False)
    details = Column(Text, nullable=False)
    raw_payload = Column(Text, nullable=True)
