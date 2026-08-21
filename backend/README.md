# AI-Based Autonomous Railway Safety System - Backend Process

A backend system implementing continuous train tracking, signal verification, physics-based collision prediction, and automatic emergency braking (AEB) actuation.

## Architecture Overview

1. **Sensing Layer (`app/services/sensing_service.py`)**:
   - Ingests GPS/GNSS position, speed, and heading telemetry.
   - Applies track-side RFID / Balise marker position calibration.
   - Dual-channel signal aspect ingestion (camera visual AI aspect vs. digital interlocking state).

2. **Communication Layer (`app/api/websocket.py`)**:
   - Real-time WebSocket broadcasting server (`/ws/live-monitoring`).
   - Low-latency telemetry bus simulation.

3. **AI Processing Layer**:
   - **Signal Verification Engine (`app/services/signal_verification.py`)**: Cross-checks visual signal aspects against digital interlocking interlocking states; flags aspect mismatches & tampering.
   - **Collision Prediction Engine (`app/services/collision_prediction.py`)**: Physics kinematic braking model ($d = v \cdot t_{\text{reaction}} + \frac{v^2}{2a}$ adjusted for track gradient); forecasts head-on / rear-end path overlaps and red light overspeed hazards.

4. **Control & Actuation Layer (`app/services/control_actuation.py`)**:
   - Dynamically calculates braking intensity (0-100%) and target speed limits.
   - Triggers Automatic Emergency Braking (AEB) commands, bypassing manual driver intervention.

5. **Audit Logging & Analytics (`app/services/audit_logger.py`, `app/services/analytics_service.py`)**:
   - SQLite audit trail database for compliance review.
   - Real dataset reviewer for track network topology, signals, and fleet specifications.

---

## Quick Start & Review Commands

### 1. Run Data Review & Safety Evaluation CLI
To review the real dataset and execute simulation test cases from the command line:
```bash
py -3 run_review.py
```

### 2. Run Automated PyTest Suite
To run the safety system test suite:
```bash
py -3 -m pytest tests/
```

### 3. Launch REST & WebSocket Server
To launch the FastAPI backend server on `http://localhost:8000`:
```bash
py -3 main.py
```
Open `http://localhost:8000/docs` in your browser for the interactive OpenAPI documentation.
