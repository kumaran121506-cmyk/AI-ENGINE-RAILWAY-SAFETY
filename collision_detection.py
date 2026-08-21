train_1_speed = 90
train_2_speed = 85

distance = 500
safe_distance = 600

print("=" * 50)
print("       COLLISION RISK DETECTION")
print("=" * 50)

print("Train 1 Speed :", train_1_speed, "km/h")
print("Train 2 Speed :", train_2_speed, "km/h")
print("Distance      :", distance, "m")
print("Safe Distance :", safe_distance, "m")

print("-" * 50)

if distance < safe_distance:
    risk = "HIGH"
    print("COLLISION RISK : DETECTED")
    print("RISK LEVEL     :", risk)
    print("ACTION         : SAFETY WARNING")
else:
    risk = "SAFE"
    print("COLLISION RISK : NOT DETECTED")
    print("RISK LEVEL     :", risk)
    print("ACTION         : NORMAL")

print("=" * 50)