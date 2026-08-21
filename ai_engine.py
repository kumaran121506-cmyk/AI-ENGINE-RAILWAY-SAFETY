import pandas as pd
import pickle

# Load trained AI model
with open("railway_risk_model.pkl", "rb") as file:
    model = pickle.load(file)

with open("model_features.pkl", "rb") as file:
    features = pickle.load(file)


# ==============================
# RAILWAY INPUT DATA
# ==============================

train_speed = 115
speed_limit = 100

distance = 450
braking_distance = 520

signal_status = "RED"
direction = "NORTH"


# ==============================
# OVERSPEED DETECTION
# ==============================

if train_speed > speed_limit:
    overspeed = True
    excess_speed = train_speed - speed_limit
else:
    overspeed = False
    excess_speed = 0


# ==============================
# COLLISION RISK
# ==============================

if distance < braking_distance:
    collision_risk = True
else:
    collision_risk = False


# ==============================
# SIGNAL VERIFICATION
# ==============================

if signal_status == "RED":
    signal_risk = True
else:
    signal_risk = False


# ==============================
# AI MODEL PREDICTION
# ==============================

new_data = pd.DataFrame([{
    "train_speed": train_speed,
    "speed_limit": speed_limit,
    "distance": distance,
    "braking_distance": braking_distance,
    "signal_status": signal_status,
    "direction": direction
}])

new_data = pd.get_dummies(new_data)
new_data = new_data.reindex(columns=features, fill_value=0)

ai_prediction = model.predict(new_data)[0]


# ==============================
# FINAL RISK DECISION
# ==============================

if collision_risk or signal_risk or overspeed:
    final_risk = "HIGH RISK"
elif ai_prediction == "MEDIUM":
    final_risk = "MEDIUM RISK"
else:
    final_risk = "SAFE"


# ==============================
# FINAL AI ENGINE OUTPUT
# ==============================

print("=" * 55)
print("          AI RAILWAY SAFETY ENGINE")
print("=" * 55)

print("\nTRAIN INFORMATION")
print("-" * 55)

print("Train Speed       :", train_speed, "km/h")
print("Speed Limit       :", speed_limit, "km/h")
print("Distance          :", distance, "m")
print("Braking Distance  :", braking_distance, "m")
print("Signal Status     :", signal_status)
print("Direction         :", direction)

print("\nAI ANALYSIS")
print("-" * 55)

if overspeed:
    print("Overspeed         : DETECTED")
    print("Excess Speed      :", excess_speed, "km/h")
else:
    print("Overspeed         : NOT DETECTED")

if collision_risk:
    print("Collision Risk    : DETECTED")
else:
    print("Collision Risk    : NOT DETECTED")

if signal_risk:
    print("Signal Violation  : DETECTED")
else:
    print("Signal Violation  : NOT DETECTED")

print("\nAI Model Prediction:", ai_prediction)

print("\n" + "=" * 55)
print("FINAL RISK LEVEL :", final_risk)
print("=" * 55)

if final_risk == "HIGH RISK":
    print("⚠ SAFETY WARNING: IMMEDIATE ATTENTION REQUIRED")
elif final_risk == "MEDIUM RISK":
    print("⚠ CAUTION: MONITOR TRAIN CONDITION")
else:
    print("✓ STATUS: TRAIN OPERATING SAFELY")

print("=" * 55)