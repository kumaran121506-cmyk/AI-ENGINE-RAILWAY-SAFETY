import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import pickle

# Load dataset
df = pd.read_csv("railway_safety_dataset.csv")

# Input features
X = df[
    [
        "train_speed",
        "speed_limit",
        "distance",
        "braking_distance",
        "signal_status",
        "direction"
    ]
]

# Convert text values into numbers
X = pd.get_dummies(X)

# Target
y = df["risk_level"]

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Create AI model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

# Train
model.fit(X_train, y_train)

# Test
predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)

print("AI Model Training Completed!")
print("Model Accuracy:", round(accuracy * 100, 2), "%")

# Save model
with open("railway_risk_model.pkl", "wb") as file:
    pickle.dump(model, file)

# Save feature names
with open("model_features.pkl", "wb") as file:
    pickle.dump(X.columns.tolist(), file)

print("Model saved successfully!")