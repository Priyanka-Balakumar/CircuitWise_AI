import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import IsolationForest


# ============================================================
# CIRCUITWISE AI - ANOMALY DETECTION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATASET_PATH = "D:\pri\ibm\projects\ibm ai project\CircuitWise_AI_ML_Dataset_V4_4.csv"


# ------------------------------------------------------------
# ML FEATURES
# Must match the V4.4 dataset
# ------------------------------------------------------------

FEATURES = [
    "component_count",
    "system_voltage_v",
    "analysis_period_min",
    "active_duration_min",
    "sleep_duration_min",
    "peak_duration_min",
    "avg_active_current_ma",
    "avg_sleep_current_ma",
    "avg_peak_current_ma"
]


# ============================================================
# LOAD DATASET
# ============================================================

print("=" * 65)
print("          CIRCUITWISE AI - ANOMALY DETECTION")
print("=" * 65)

try:

    df = pd.read_csv(DATASET_PATH)

    print("\nDataset loaded successfully.")
    print("Dataset shape:", df.shape)

except Exception as e:

    print("\nERROR: Could not load dataset.")
    print("Reason:", e)
    raise SystemExit


# ============================================================
# CHECK REQUIRED FEATURES
# ============================================================

missing_features = [
    feature
    for feature in FEATURES
    if feature not in df.columns
]

if missing_features:

    print("\nERROR: Missing required features:")

    for feature in missing_features:
        print("-", feature)

    raise SystemExit


# ============================================================
# PREPARE DATA
# ============================================================

X = df[FEATURES].copy()

X = X.replace([np.inf, -np.inf], np.nan)

X = X.fillna(0)


# ============================================================
# TRAIN ISOLATION FOREST
# ============================================================

print("\nTraining anomaly detection model...")

anomaly_model = IsolationForest(
    n_estimators=200,
    contamination=0.05,
    random_state=42
)

anomaly_model.fit(X)


# ============================================================
# PREDICT ANOMALIES
# ============================================================

df["anomaly_prediction"] = anomaly_model.predict(X)

df["anomaly_score"] = anomaly_model.decision_function(X)


# Isolation Forest:
#
#  1  = normal
# -1  = anomaly

df["anomaly_status"] = df["anomaly_prediction"].map({
    1: "NORMAL",
    -1: "ANOMALY"
})


# ============================================================
# RESULTS
# ============================================================

total_rows = len(df)

normal_count = (
    df["anomaly_status"] == "NORMAL"
).sum()

anomaly_count = (
    df["anomaly_status"] == "ANOMALY"
).sum()


print("\n" + "=" * 65)
print("ANOMALY DETECTION RESULTS")
print("=" * 65)

print(
    f"Total configurations : {total_rows}"
)

print(
    f"Normal configurations: {normal_count}"
)

print(
    f"Anomalies detected   : {anomaly_count}"
)

print(
    f"Anomaly percentage   : "
    f"{(anomaly_count / total_rows) * 100:.2f}%"
)


# ============================================================
# DISPLAY ANOMALOUS CONFIGURATIONS
# ============================================================

anomalies = df[
    df["anomaly_status"] == "ANOMALY"
].copy()


print("\n" + "=" * 65)
print("DETECTED ANOMALIES")
print("=" * 65)


if len(anomalies) == 0:

    print("\nNo anomalies detected.")

else:

    # Sort by anomaly score.
    # Lower score = more unusual.

    anomalies = anomalies.sort_values(
        by="anomaly_score"
    )

    display_columns = [
        "configuration_id",
        "components",
        "component_count",
        "system_voltage_v",
        "analysis_period_min",
        "active_duration_min",
        "sleep_duration_min",
        "peak_duration_min",
        "avg_active_current_ma",
        "avg_sleep_current_ma",
        "avg_peak_current_ma",
        "calculated_energy_mwh",
        "target_energy_mwh",
        "anomaly_score"
    ]

    # Keep only columns that actually exist
    display_columns = [
        column
        for column in display_columns
        if column in anomalies.columns
    ]

    print(
        anomalies[display_columns]
        .head(20)
        .to_string(index=False)
    )


# ============================================================
# MOST ANOMALOUS CONFIGURATION
# ============================================================

if len(anomalies) > 0:

    most_anomalous = anomalies.iloc[0]

    print("\n" + "=" * 65)
    print("MOST UNUSUAL CONFIGURATION")
    print("=" * 65)

    if "configuration_id" in anomalies.columns:
        print(
            "Configuration ID:",
            most_anomalous["configuration_id"]
        )

    if "components" in anomalies.columns:
        print(
            "Components:",
            most_anomalous["components"]
        )

    if "calculated_energy_mwh" in anomalies.columns:
        print(
            "Calculated energy:",
            f"{most_anomalous['calculated_energy_mwh']:.4f} mWh"
        )

    if "target_energy_mwh" in anomalies.columns:
        print(
            "Target energy:",
            f"{most_anomalous['target_energy_mwh']:.4f} mWh"
        )

    print(
        "Anomaly score:",
        f"{most_anomalous['anomaly_score']:.6f}"
    )


# ============================================================
# SAVE RESULTS
# ============================================================

OUTPUT_DIR = BASE_DIR / "data"

# Create data folder if it does not exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = (
    OUTPUT_DIR
    / "CircuitWise_AI_Anomaly_Results.csv"
)

df.to_csv(
    OUTPUT_PATH,
    index=False
)

print("\n" + "=" * 65)
print("ANOMALY ANALYSIS COMPLETE")
print("=" * 65)

print("\nResults saved to:")
print(OUTPUT_PATH)
