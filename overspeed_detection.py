train_speed = 115
speed_limit = 100

print("=" * 45)
print("       OVERSPEED DETECTION")
print("=" * 45)

print("Train Speed :", train_speed, "km/h")
print("Speed Limit :", speed_limit, "km/h")

if train_speed > speed_limit:
    excess_speed = train_speed - speed_limit
    print("-" * 45)
    print("STATUS      : OVERSPEED DETECTED")
    print("Excess Speed:", excess_speed, "km/h")
    print("RISK        : HIGH")
else:
    print("-" * 45)
    print("STATUS      : SPEED NORMAL")
    print("RISK        : SAFE")

print("=" * 45)