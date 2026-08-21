"""
Analytics & Real Data Reviewer Service: Loads real network datasets, train specifications,
and historical events for model review and reporting.
"""

import os
import json
from typing import Dict, Any, List
from app.config import DATA_DIR

class AnalyticsService:
    def __init__(self):
        self.track_data = self._load_json("real_track_network.json")
        self.fleet_data = self._load_json("train_fleet_data.json")
        self.historical_data = self._load_json("historical_telemetry.json")

    def _load_json(self, filename: str) -> Dict[str, Any]:
        filepath = os.path.join(DATA_DIR, filename)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def get_network_overview(self) -> Dict[str, Any]:
        corridors = self.track_data.get("corridors", [])
        total_segments = sum(len(c.get("segments", [])) for c in corridors)
        total_signals = sum(
            sum(len(s.get("signals", [])) for s in c.get("segments", []))
            for c in corridors
        )
        return {
            "corridors_count": len(corridors),
            "segments_count": total_segments,
            "signals_count": total_signals,
            "corridors": corridors
        }

    def get_fleet_specifications(self) -> List[Dict[str, Any]]:
        return self.fleet_data.get("fleet", [])

    def get_historical_review_data(self) -> List[Dict[str, Any]]:
        return self.historical_data.get("historical_events", [])
