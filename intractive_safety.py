import joblib
import pandas as pd

# Load trained model
model = joblib.load("railway_risk_model.pkl")

print("=" * 55)
print("        AI RAILWAY SAFETY SYSTEM")
print("=" * 55)

# User inputs
speed = float(input("Enter Train Speed (km/h): "))
speed_limit = float(input("Enter Speed Limit (km/h): "))
distance = float(input("Enter Distance to Obstacle (m): "))
braking_distance = float(input("Enter Braking Distance (m): "))

signal = input("Enter Signal Status (RED/GREEN/YELLOW): ").upper()
direction = input("Enter Train Direction (NORTH/SOUTH/EAST/WEST): ").upper()

# Safety detection
overspeed = speed > speed_limit
collision_risk = braking_distance > distance
signal_violation = signal == "RED"

# Encode signal
signal_green = 1 if signal == "GREEN" else 0
signal_red = 1 if signal == "RED" else 0
signal_yellow = 1 if signal == "YELLOW" else 0

# Encode direction
direction_east = 1 if direction == "EAST" else 0
direction_north = 1 if direction == "NORTH" else 0
direction_south = 1 if direction == "SOUTH" else 0
direction_west = 1 if direction == "WEST" else 0

# Create model input
input_data = pd.DataFrame([{
    "train_speed": speed,
    "speed_limit": speed_limit,
    "distance": distance,
    "braking_distance": braking_distance,
    "signal_status_GREEN": signal_green,
    "signal_status_RED": signal_red,
    "signal_status_YELLOW": signal_yellow,
    "direction_EAST": direction_east,
    "direction_NORTH": direction_north,
    "direction_SOUTH": direction_south,
    "direction_WEST": direction_west
}])

# AI prediction
prediction = model.predict(input_data)[0]

print("\n" + "=" * 55)
print("              AI ANALYSIS")
print("=" * 55)

print(f"Overspeed         : {'DETECTED' if overspeed else 'NORMAL'}")
print(f"Collision Risk    : {'DETECTED' if collision_risk else 'LOW'}")
print(f"Signal Violation  : {'DETECTED' if signal_violation else 'NORMAL'}")
print(f"AI Model Prediction: {str(prediction).upper()}")

print("=" * 55)

if str(prediction).upper() == "HIGH":
    print("FINAL RISK LEVEL : HIGH RISK")
    print("WARNING: IMMEDIATE ATTENTION REQUIRED")
elif str(prediction).upper() == "MEDIUM":
    print("FINAL RISK LEVEL : MEDIUM RISK")
    print("WARNING: CAUTION REQUIRED")
else:
    print("FINAL RISK LEVEL : LOW RISK")
    print("STATUS: TRAIN OPERATING SAFELY")

print("=" * 55)