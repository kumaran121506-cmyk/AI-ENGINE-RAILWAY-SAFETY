"""
Control & Actuation Layer Service:
Issues automatic braking commands, target speed limits, and solenoid actuation signals.
Bypasses manual driver intervention when safety thresholds are breached.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from app.models.schemas import BrakingCommand, CollisionRiskResult, SignalVerificationResult
from app.config import RISK_LEVEL_CRITICAL, RISK_LEVEL_WARNING

class ControlActuationService:
    def issue_braking_command(
        self,
        train_id: str,
        current_speed_kmh: float,
        collision_risk: CollisionRiskResult,
        signal_verification: Optional[SignalVerificationResult] = None
    ) -> Optional[BrakingCommand]:
        """
        Determines and issues physical braking command based on risk analysis.
        """
        needs_emergency_brake = False
        braking_intensity = 0.0
        target_speed = current_speed_kmh
        reason_parts = []

        # Check Signal Verification mismatch or visual stop
        if signal_verification and signal_verification.mismatch_detected:
            if signal_verification.alert_level == RISK_LEVEL_CRITICAL:
                needs_emergency_brake = True
                braking_intensity = 100.0
                target_speed = 0.0
                reason_parts.append(f"Critical Signal Mismatch: {signal_verification.details}")
            elif signal_verification.alert_level == RISK_LEVEL_WARNING:
                braking_intensity = 40.0
                target_speed = min(current_speed_kmh, 30.0) # Reduce to caution speed
                reason_parts.append(f"Signal Advisory: {signal_verification.details}")

        # Check Collision Risk Engine Output
        if collision_risk.risk_level == RISK_LEVEL_CRITICAL or collision_risk.action_required == "EMERGENCY_BRAKE":
            needs_emergency_brake = True
            braking_intensity = 100.0
            target_speed = 0.0
            reason_parts.append(f"Collision Risk: {collision_risk.explanation}")
        elif collision_risk.risk_level == RISK_LEVEL_WARNING or collision_risk.action_required == "ADVISORY_SLOW":
            if braking_intensity < 50.0:
                braking_intensity = 50.0
                target_speed = min(current_speed_kmh, 60.0)
            reason_parts.append(f"Speed Advisory: {collision_risk.explanation}")

        # If braking action is required, generate command
        if braking_intensity > 0.0:
            return BrakingCommand(
                command_id=f"ACT-{uuid.uuid4().hex[:8].upper()}",
                train_id=train_id,
                timestamp=datetime.now(timezone.utc),
                risk_level=RISK_LEVEL_CRITICAL if needs_emergency_brake else RISK_LEVEL_WARNING,
                emergency_brake_engaged=needs_emergency_brake,
                braking_intensity_percent=braking_intensity,
                target_speed_kmh=target_speed,
                calculated_stopping_distance_m=collision_risk.calculated_stopping_distance_meters,
                reason=" | ".join(reason_parts)
            )

        return None
