"""
CLI Data Review & Process Evaluation Tool:
Executes full backend pipeline on real dataset samples and prints formatted safety review reports.
"""

import json
from app.services.analytics_service import AnalyticsService
from app.simulator.scenario_runner import ScenarioRunner
from app.services.audit_logger import AuditLogger
from app.database.session import SessionLocal
from app.database.repository import DatabaseRepository

def print_separator(title: str):
    print("\n" + "=" * 80)
    print(f"  {title.upper()}")
    print("=" * 80)

def main():
    analytics = AnalyticsService()
    runner = ScenarioRunner()
    audit_log = AuditLogger()

    print_separator("1. Real Track Network & Fleet Specifications Review")
    network = analytics.get_network_overview()
    fleet = analytics.get_fleet_specifications()

    print(f"[+] Active Corridors Loaded: {network['corridors_count']}")
    for c in network['corridors']:
        print(f"    - Corridor: {c['name']} (Length: {c['total_length_km']} km, Max Speed: {c['max_speed_kmh']} km/h)")
        for s in c['segments']:
            print(f"      * Segment {s['segment_id']}: {s['start_km']}km -> {s['end_km']}km | Speed Limit: {s['speed_limit_kmh']} km/h | Signals: {len(s['signals'])}")

    print(f"\n[+] Registered Train Fleet Specifications: {len(fleet)}")
    for train in fleet:
        print(f"    - {train['train_id']} ({train['name']}): Mass={train['total_mass_tonnes']}t, Length={train['length_meters']}m, Emergency Decel={train['emergency_decel_ms2']} m/s²")

    print_separator("2. AI Signal Verification & Red-Light Protection Review")
    signal_results = runner.run_signal_mismatch_scenario()
    for res in signal_results:
        print(f"Scenario: {res['scenario_name']}")
        print(f"Train ID: {res['train_id']} at Speed: {res['speed_kmh']} km/h (Pos: {res['position_km']} km)")
        print(f"Signal Check: Digital={res['signal_verification']['digital_state']} vs Camera Visual={res['signal_verification']['visual_aspect']}")
        print(f"Alert Level: {res['signal_verification']['alert_level']}")
        print(f"Details: {res['signal_verification']['details']}")
        if res['braking_command']:
            cmd = res['braking_command']
            print(f"-> Physical Actuation Triggered: {cmd['command_id']}")
            print(f"   Emergency Brake Engaged: {cmd['emergency_brake_engaged']} | Intensity: {cmd['braking_intensity_percent']}% | Target Speed: {cmd['target_speed_kmh']} km/h")
            print(f"   Calculated Stopping Distance: {cmd['calculated_stopping_distance_m']}m")

    print_separator("3. AI Physics Collision Prediction Review (Head-On Scenario)")
    collision_results = runner.run_head_on_collision_scenario()
    for res in collision_results:
        print(f"Scenario: {res['scenario_name']}")
        t1 = res['train_1']
        t2 = res['train_2']
        print(f"[Train 1: {t1['id']}] Risk Level: {t1['risk']['risk_level']} | Explanation: {t1['risk']['explanation']}")
        if t1['braking_command']:
            print(f"   -> AEB Actuated: Intensity={t1['braking_command']['braking_intensity_percent']}%, Target Speed={t1['braking_command']['target_speed_kmh']} km/h")

        print(f"[Train 2: {t2['id']}] Risk Level: {t2['risk']['risk_level']} | Explanation: {t2['risk']['explanation']}")
        if t2['braking_command']:
            print(f"   -> AEB Actuated: Intensity={t2['braking_command']['braking_intensity_percent']}%, Target Speed={t2['braking_command']['target_speed_kmh']} km/h")

    print_separator("4. Compliance Audit Logs (SQL Database Persistence)")
    db = SessionLocal()
    try:
        repo = DatabaseRepository()
        db_logs = repo.get_audit_logs(db=db, limit=5)
        print(f"[+] Recent Audit Log Records in Database: {len(db_logs)}")
        for log in db_logs:
            print(f"[{log.timestamp}] ID:{log.id} | Event:{log.event_type} | Train:{log.train_id} | Risk:{log.risk_level}")
            print(f"    Detail: {log.details}")
    finally:
        db.close()

    print_separator("Backend Process Review Complete - All Systems Operational")

if __name__ == "__main__":
    main()
