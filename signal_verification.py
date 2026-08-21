signal_status = "RED"

print("=" * 45)
print("       RAILWAY SIGNAL VERIFICATION")
print("=" * 45)

print("Detected Signal :", signal_status)

print("-" * 45)

if signal_status == "GREEN":
    print("SIGNAL STATUS   : SAFE")
    print("ACTION          : TRAIN CAN PROCEED")

elif signal_status == "YELLOW":
    print("SIGNAL STATUS   : CAUTION")
    print("ACTION          : REDUCE SPEED")

elif signal_status == "RED":
    print("SIGNAL STATUS   : DANGER")
    print("ACTION          : STOP TRAIN")

else:
    print("SIGNAL STATUS   : UNKNOWN")
    print("ACTION          : SAFETY CHECK REQUIRED")

print("=" * 45)