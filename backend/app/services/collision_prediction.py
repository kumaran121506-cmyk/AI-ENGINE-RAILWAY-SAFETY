"""
AI Processing Layer - Collision Prediction Engine:
Physics-based trajectory projection and collision risk calculation.
Calculates dynamic stopping distance, headway margins, and path intersections.
"""

import math
from typing import Dict, Any, List, Optional
from app.models.schemas import TrainTelemetryInput, CollisionRiskResult
from app.config import (
    DEFAULT_REACTION_TIME_SEC,
    DEFAULT_FRICTION_COEFF,
    GRAVITY_ACCEL,
    SAFE_MARGIN_METERS,
    RISK_LEVEL_NORMAL,
    RISK_LEVEL_WARNING,
    RISK_LEVEL_CRITICAL,
    ASPECT_STOP
)

class CollisionPredictionEngine:
    def calculate_stopping_distance(
        self,
        speed_kmh: float,
        decel_ms2: float = 1.2,
        reaction_time_sec: float = DEFAULT_REACTION_TIME_SEC,
        gradient_percent: float = 0.0
    ) -> float:
        """
        Calculates total emergency stopping distance in meters:
        d_stop = (v * t_reaction) + [ v^2 / (2 * (a_brake + g * gradient/100)) ]
        """
        if speed_kmh <= 0:
            return 0.0

        v_ms = speed_kmh / 3.6
        reaction_dist = v_ms * reaction_time_sec

        # Effective deceleration adjusted for gradient (positive gradient = uphill helps braking, negative = downhill lengthens distance)
        effective_decel = decel_ms2 + (GRAVITY_ACCEL * (gradient_percent / 100.0))
        effective_decel = max(0.2, effective_decel) # Prevent division by zero or negative deceleration

        braking_dist = (v_ms ** 2) / (2.0 * effective_decel)
        return round(reaction_dist + braking_dist, 2)

    def evaluate_train_risk(
        self,
        current_train: Dict[str, Any],
        other_trains: List[Dict[str, Any]],
        signal_state: Optional[Dict[str, Any]] = None,
        gradient_percent: float = 0.0,
        segment_speed_limit_kmh: float = 160.0
    ) -> CollisionRiskResult:
        train_id = current_train["train_id"]
        speed_kmh = current_train["speed_kmh"]
        position_km = current_train["position_km"]
        segment_id = current_train["track_segment_id"]

        # Calculate train's stopping distance
        stopping_dist_m = self.calculate_stopping_distance(
            speed_kmh=speed_kmh,
            gradient_percent=gradient_percent
        )

        # 1. Check Overspeed Condition
        if speed_kmh > (segment_speed_limit_kmh * 1.05):
            return CollisionRiskResult(
                train_id=train_id,
                calculated_stopping_distance_meters=stopping_dist_m,
                risk_level=RISK_LEVEL_WARNING,
                action_required="ADVISORY_SLOW",
                explanation=f"Overspeed detected! Train traveling at {speed_kmh:.1f} km/h (Limit: {segment_speed_limit_kmh} km/h)."
            )

        # 2. Check Signal Distance & Violation Risk
        if signal_state:
            digital_state = signal_state.get("digital_state", "")
            visual_aspect = signal_state.get("visual_aspect", "")
            signal_km = signal_state.get("km_marker", 0.0)

            # Distance to upcoming signal in meters
            dist_to_signal_m = (signal_km - position_km) * 1000.0

            # If signal requires stopping (STOP aspect) and train is within stopping distance horizon
            if (digital_state == ASPECT_STOP or visual_aspect == ASPECT_STOP) and dist_to_signal_m > 0:
                if (stopping_dist_m + SAFE_MARGIN_METERS) >= dist_to_signal_m:
                    return CollisionRiskResult(
                        train_id=train_id,
                        calculated_stopping_distance_meters=stopping_dist_m,
                        risk_level=RISK_LEVEL_CRITICAL,
                        action_required="EMERGENCY_BRAKE",
                        explanation=f"Imminent Signal Violation! Train at {position_km:.2f} km approaching STOP signal at {signal_km:.2f} km. Distance ({dist_to_signal_m:.1f}m) < required stopping distance + safety margin ({stopping_dist_m + SAFE_MARGIN_METERS:.1f}m)."
                    )

        # 3. Check Train-to-Train Collision Risk (V2V / Central AI tracking)
        for other in other_trains:
            if other["train_id"] == train_id:
                continue

            # If on same segment or adjacent path
            if other["track_segment_id"] == segment_id:
                other_pos_km = other["position_km"]
                other_speed_kmh = other["speed_kmh"]
                other_stopping_dist_m = self.calculate_stopping_distance(
                    speed_kmh=other_speed_kmh,
                    gradient_percent=gradient_percent
                )

                distance_gap_m = abs(position_km - other_pos_km) * 1000.0
                combined_safe_dist_m = stopping_dist_m + other_stopping_dist_m + SAFE_MARGIN_METERS

                # Check if moving towards each other (Head-on) or trailing too close (Rear-end)
                is_head_on = (position_km < other_pos_km and current_train.get("heading_deg", 0) < 180 and other.get("heading_deg", 180) >= 180) or \
                             (position_km > other_pos_km and current_train.get("heading_deg", 180) >= 180 and other.get("heading_deg", 0) < 180)

                if distance_gap_m <= combined_safe_dist_m:
                    risk_lvl = RISK_LEVEL_CRITICAL if (is_head_on or distance_gap_m < (combined_safe_dist_m * 0.7)) else RISK_LEVEL_WARNING
                    action = "EMERGENCY_BRAKE" if risk_lvl == RISK_LEVEL_CRITICAL else "ADVISORY_SLOW"
                    collision_type = "Head-on" if is_head_on else "Rear-end / Catch-up"

                    return CollisionRiskResult(
                        train_id=train_id,
                        other_train_id=other["train_id"],
                        distance_gap_meters=round(distance_gap_m, 1),
                        calculated_stopping_distance_meters=stopping_dist_m,
                        risk_level=risk_lvl,
                        action_required=action,
                        explanation=f"Imminent {collision_type} Collision Risk between {train_id} and {other['train_id']}! Distance gap: {distance_gap_m:.1f}m (Required safe clearance: {combined_safe_dist_m:.1f}m)."
                    )

        # Default normal operation
        return CollisionRiskResult(
            train_id=train_id,
            calculated_stopping_distance_meters=stopping_dist_m,
            risk_level=RISK_LEVEL_NORMAL,
            action_required="NONE",
            explanation="Normal operation. Trajectory path clear and within safe headway margins."
        )
