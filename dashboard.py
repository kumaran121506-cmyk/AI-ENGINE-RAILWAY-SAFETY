import streamlit as st
import joblib
import pandas as pd

# Load trained AI model
model = joblib.load("railway_risk_model.pkl")

st.set_page_config(
    page_title="AI Railway Safety System",
    page_icon="🚆",
    layout="wide"
)

st.title("🚆 AI Railway Safety System")
st.caption("AI-based Autonomous Railway Risk Monitoring")

st.divider()

# Input section
st.subheader("Train Information")

col1, col2 = st.columns(2)

with col1:
    speed = st.number_input("Train Speed (km/h)", min_value=0.0, value=115.0)
    speed_limit = st.number_input("Speed Limit (km/h)", min_value=0.0, value=100.0)
    distance = st.number_input("Distance to Obstacle (m)", min_value=0.0, value=450.0)

with col2:
    braking_distance = st.number_input(
        "Braking Distance (m)",
        min_value=0.0,
        value=520.0
    )

    signal = st.selectbox(
        "Signal Status",
        ["RED", "YELLOW", "GREEN"]
    )

    direction = st.selectbox(
        "Train Direction",
        ["NORTH", "SOUTH", "EAST", "WEST"]
    )

st.divider()

if st.button("🔍 ANALYZE SAFETY", use_container_width=True):

    # Safety calculations
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

    # Model input
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
    prediction = str(model.predict(input_data)[0]).upper()

    st.subheader("AI Safety Analysis")

    a, b, c = st.columns(3)

    with a:
        st.metric(
            "Overspeed",
            "DETECTED" if overspeed else "NORMAL"
        )

    with b:
        st.metric(
            "Collision Risk",
            "DETECTED" if collision_risk else "LOW"
        )

    with c:
        st.metric(
            "Signal Violation",
            "DETECTED" if signal_violation else "NORMAL"
        )

    st.divider()

    if prediction == "HIGH":
        st.error("🚨 HIGH RISK — IMMEDIATE ATTENTION REQUIRED")
    elif prediction == "MEDIUM":
        st.warning("⚠️ MEDIUM RISK — CAUTION REQUIRED")
    else:
        st.success("✅ LOW RISK — TRAIN OPERATING SAFELY")

    st.info(f"AI Model Prediction: **{prediction}**")