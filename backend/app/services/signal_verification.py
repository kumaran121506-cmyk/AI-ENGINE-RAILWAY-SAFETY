"""
AI Processing Layer - Signal Verification Engine:
Cross-checks visual signal camera feeds against digital interlocking interlocking states.
Flag mismatches, aspect corruption, or tampering attempts.
"""

from app.models.schemas import SignalAspectInput, SignalVerificationResult
from app.config import (
    RISK_LEVEL_NORMAL,
    RISK_LEVEL_WARNING,
    RISK_LEVEL_CRITICAL,
    ASPECT_STOP,
    ASPECT_CAUTION,
    ASPECT_PROCEED
)

class SignalVerificationEngine:
    def verify_signal(self, signal_data: SignalAspectInput) -> SignalVerificationResult:
        digital = signal_data.interlocking_digital_state.upper()
        visual = signal_data.camera_visual_aspect.upper()
        confidence = signal_data.confidence_score

        # Case 1: Exact match
        if digital == visual:
            return SignalVerificationResult(
                signal_id=signal_data.signal_id,
                is_valid=True,
                digital_state=digital,
                visual_aspect=visual,
                mismatch_detected=False,
                alert_level=RISK_LEVEL_NORMAL,
                details=f"Signal integrity verified. Both digital interlocking and camera visual report '{digital}' with {confidence*100:.1f}% confidence."
            )

        # Case 2: Visual aspect is STOP, but digital states PROCEED/CAUTION (Possibility of un-signaled obstacle / physical signal fault)
        if visual == ASPECT_STOP and digital != ASPECT_STOP:
            return SignalVerificationResult(
                signal_id=signal_data.signal_id,
                is_valid=False,
                digital_state=digital,
                visual_aspect=visual,
                mismatch_detected=True,
                alert_level=RISK_LEVEL_CRITICAL,
                details=f"SAFETY HAZARD: Trackside camera detected visual STOP aspect, but interlocking reports '{digital}'. Failsafe rule triggers immediate caution/stop."
            )

        # Case 3: Digital is STOP, but visual reports PROCEED/CAUTION (Possible optical glare, dirty lens, or spoofing)
        if digital == ASPECT_STOP and visual != ASPECT_STOP:
            return SignalVerificationResult(
                signal_id=signal_data.signal_id,
                is_valid=False,
                digital_state=digital,
                visual_aspect=visual,
                mismatch_detected=True,
                alert_level=RISK_LEVEL_CRITICAL,
                details=f"CRITICAL SIGNAL MISMATCH: Interlocking signals RED (STOP), but visual camera sees '{visual}'. Trusting digital interlocking STOP state."
            )

        # Case 4: Discrepancy between CAUTION and PROCEED
        return SignalVerificationResult(
            signal_id=signal_data.signal_id,
            is_valid=False,
            digital_state=digital,
            visual_aspect=visual,
            mismatch_detected=True,
            alert_level=RISK_LEVEL_WARNING,
            details=f"SIGNAL ASPECT MISMATCH: Digital '{digital}' vs Visual '{visual}'. Downgrading target speed to CAUTION speed limit."
        )
