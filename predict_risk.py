import pandas as pd
import pickle

# Load trained model
with open("railway_risk_model.pkl", "rb") as file:
    model = pickle.load(file)

# Load feature names
with open("model_features.pkl", "rb") as file:
    features = pickle.load(file)

# New railway situation
new_data = pd.DataFrame([{
    "train_speed": 115,
    "speed_limit": 100,
    "distance": 450,
    "braking_distance": 520,
    "signal_status": "RED",
    "direction": "NORTH"
}])

# Convert categorical data
new_data = pd.get_dummies(new_data)

# Match training columns
new_data = new_data.reindex(columns=features, fill_value=0)

# Predict
prediction = model.predict(new_data)[0]

print("=" * 45)
print("       AI RAILWAY SAFETY SYSTEM")
print("=" * 45)

print("Train Speed       :", 115, "km/h")
print("Speed Limit       :", 100, "km/h")
print("Distance          :", 450, "m")
print("Braking Distance  :", 520, "m")
print("Signal Status     :", "RED")
print("Direction         :", "NORTH")

print("-" * 45)
print("AI RISK PREDICTION:", prediction)

if prediction == "HIGH":
    print("WARNING: HIGH RISK DETECTED!")
elif prediction == "MEDIUM":
    print("WARNING: MEDIUM RISK")
else:
    print("STATUS: SAFE")

print("=" * 45)