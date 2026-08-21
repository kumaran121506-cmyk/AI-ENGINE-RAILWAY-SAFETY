"""
Configuration settings for AI-Based Autonomous Railway Safety System.
"""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "app", "data")
DB_PATH = os.path.join(BASE_DIR, "railway_safety_audit.db")

# Safety & Physics Constants
DEFAULT_REACTION_TIME_SEC = 0.25      # System electronic reaction + solenoid delay (s)
DEFAULT_FRICTION_COEFF = 0.35         # Standard steel-on-steel rail friction coefficient
GRAVITY_ACCEL = 9.81                  # m/s^2
SAFE_MARGIN_METERS = 150.0            # Minimum required clearance distance between trains (m)
OVERSPEED_THRESHOLD_RATIO = 1.05     # 5% above speed limit triggers warning/braking

# Risk Assessment Weighting & Thresholds
RISK_LEVEL_NORMAL = "NORMAL"
RISK_LEVEL_WARNING = "WARNING"
RISK_LEVEL_CRITICAL = "CRITICAL"

# Signal Aspects
ASPECT_STOP = "STOP"          # Red aspect
ASPECT_CAUTION = "CAUTION"    # Yellow aspect
ASPECT_PROCEED = "PROCEED"    # Green aspect

# WebSockets & Server Config
HOST = "0.0.0.0"
PORT = 8000
