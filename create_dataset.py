import pandas as pd
import random

data = []

for i in range(5000):
    train_speed = random.randint(40, 130)
    speed_limit = random.choice([80, 90, 100, 110, 120])
    distance = random.randint(100, 2000)
    braking_distance = random.randint(100, 800)
    signal_status = random.choice(["GREEN", "YELLOW", "RED"])
    direction = random.choice(["NORTH", "SOUTH", "EAST", "WEST"])

    risk_score = 0

    if train_speed > speed_limit:
        risk_score += 30

    if distance < braking_distance:
        risk_score += 40

    if signal_status == "RED":
        risk_score += 30
    elif signal_status == "YELLOW":
        risk_score += 10

    if risk_score >= 70:
        risk_level = "HIGH"
    elif risk_score >= 30:
        risk_level = "MEDIUM"
    else:
        risk_level = "SAFE"

    data.append([
        train_speed,
        speed_limit,
        distance,
        braking_distance,
        signal_status,
        direction,
        risk_score,
        risk_level
    ])

columns = [
    "train_speed",
    "speed_limit",
    "distance",
    "braking_distance",
    "signal_status",
    "direction",
    "risk_score",
    "risk_level"
]

df = pd.DataFrame(data, columns=columns)

df.to_csv("railway_safety_dataset.csv", index=False)

print("Railway safety dataset created successfully!")
print("Total records:", len(df))
print(df.head())