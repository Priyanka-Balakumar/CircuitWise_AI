
# ============================================================
# CIRCUITWISE AI — BOB CONTEXT EXPORT
# export_results.py
#
# Reads the two engine-generated CSV files and populates the
# anomaly_detection and optimization sections of
# bob_context/circuitwise_results.json.
#
# Run AFTER ml/anomaly_detection.py and ml/optimizer.py.
# Does NOT modify any existing engine file.
# ============================================================

import json
import os
import pandas as pd

from datetime import datetime, timezone
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

ANOMALY_CSV = BASE_DIR / "data" / "CircuitWise_AI_Anomaly_Results.csv"
OPTIMIZATION_CSV = BASE_DIR / "data" / "CircuitWise_AI_Optimization_Results.csv"
OUTPUT_JSON = Path(__file__).resolve().parent / "circuitwise_results.json"


# ============================================================
# JSON SKELETON
# (engineering_calculation and ml_prediction are filled by
#  export_prediction.py — left as null here)
# ============================================================

def build_skeleton():
    return {
        "export_timestamp": datetime.now(timezone.utc).isoformat(),
        "project": "CircuitWise AI V4.4",
        "data_status": {
            "dataset": "synthetic/calculated — generated from datasheet values using P=VxI, E=Pxt; NOT validated against physical hardware",
            "model": "RandomForestRegressor(n_estimators=200, random_state=42) trained on V4.4 synthetic dataset",
            "hardware_validation": "pending — ESP32 + INA219 physical measurement planned as future work"
        },
        "engineering_calculation": {
            "system_total_energy_mwh": None,
            "system_voltage_v": None,
            "analysis_period_min": None,
            "component_count": None,
            "components": [],
            "calculation_method": "P = V x I_mA (mW);  E = P x (duration_min / 60) (mWh)"
        },
        "ml_prediction": {
            "predicted_energy_mwh": None,
            "difference_from_calculated_mwh": None,
            "difference_percent": None,
            "interpretation_band": None,
            "features_used": [
                "component_count", "system_voltage_v", "analysis_period_min",
                "active_duration_min", "sleep_duration_min", "peak_duration_min",
                "avg_active_current_ma", "avg_sleep_current_ma", "avg_peak_current_ma"
            ],
            "model": "RandomForestRegressor(n_estimators=200, random_state=42)",
            "note": "Prediction is based on synthetic training data. Not a hardware measurement."
        },
        "anomaly_detection": {
            "model": "IsolationForest(n_estimators=200, contamination=0.05, random_state=42)",
            "label_convention": "1 = NORMAL statistical pattern;  -1 = ANOMALY (statistically unusual — does NOT confirm hardware fault)",
            "total_configurations": None,
            "normal_count": None,
            "anomaly_count": None,
            "anomaly_percent": None,
            "demo_config_match": None,
            "anomalies": []
        },
        "optimization": {
            "system_current_energy_mwh": None,
            "system_optimized_energy_mwh": None,
            "system_saving_mwh": None,
            "system_reduction_percent": None,
            "constraint_note": "Minimum active time constraints respected per component. Savings are calculated/simulated estimates, not experimentally measured.",
            "components": [],
            "top_options": []
        },
        "responsible_ai": {
            "calculated_values_source": "Deterministic formulas: P = V x I_mA (mW);  E = P x (duration_min / 60) (mWh)",
            "predicted_values_source": "RandomForest ML model trained on synthetic/calculated data",
            "anomaly_values_source": "IsolationForest trained on synthetic/calculated data — statistical outlier detection only",
            "optimization_values_source": "Simulated active-time reduction scenarios (5% step increments) — not experimentally measured",
            "warning": (
                "All values are calculated or simulated using synthetic training data derived from "
                "component datasheets. No experimental hardware measurements have been taken. "
                "Hardware validation using ESP32 and INA219 is planned. "
                "These results must not be used as the sole basis for real system design without validation."
            )
        }
    }


# ============================================================
# LOAD ANOMALY CSV
# ============================================================

SESSION_INPUT = Path(__file__).resolve().parent / "session_input.json"


def load_anomaly_section(data):

    print("\nLoading anomaly results...")

    try:
        df = pd.read_csv(ANOMALY_CSV)
    except Exception as e:
        print(f"WARNING: Could not load anomaly CSV: {e}")
        return data

    total = len(df)
    normal = int((df["anomaly_status"] == "NORMAL").sum())
    anomalies = int((df["anomaly_status"] == "ANOMALY").sum())

    data["anomaly_detection"]["total_configurations"] = total
    data["anomaly_detection"]["normal_count"] = normal
    data["anomaly_detection"]["anomaly_count"] = anomalies
    data["anomaly_detection"]["anomaly_percent"] = round(anomalies / total * 100, 2) if total > 0 else 0.0

    anomaly_rows = df[df["anomaly_status"] == "ANOMALY"].sort_values("anomaly_score")
    anomaly_list = []
    for _, row in anomaly_rows.iterrows():
        anomaly_list.append({
            "configuration_id": int(row["configuration_id"]) if pd.notna(row.get("configuration_id")) else None,
            "components": str(row.get("components", "")),
            "component_count": int(row["component_count"]) if pd.notna(row.get("component_count")) else None,
            "system_voltage_v": float(row["system_voltage_v"]) if pd.notna(row.get("system_voltage_v")) else None,
            "calculated_energy_mwh": round(float(row["calculated_energy_mwh"]), 4) if pd.notna(row.get("calculated_energy_mwh")) else None,
            "anomaly_score": round(float(row["anomaly_score"]), 6) if pd.notna(row.get("anomaly_score")) else None,
            "anomaly_status": str(row["anomaly_status"])
        })
    data["anomaly_detection"]["anomalies"] = anomaly_list

    # Find the closest matching row to the demo session
    demo_match = None
    try:
        if SESSION_INPUT.exists():
            with open(SESSION_INPUT, "r", encoding="utf-8") as f:
                session = json.load(f)
            demo_cc = len(session.get("components", []))
            demo_v = float(session.get("system_voltage_v", 3.3))
            demo_t = float(session.get("analysis_period_min", 60))

            df_num = df.copy()
            df_num["_dist"] = (
                (df_num["component_count"] - demo_cc).abs() * 10
                + (df_num["system_voltage_v"] - demo_v).abs() * 5
                + (df_num["analysis_period_min"] - demo_t).abs() / 60.0
            )
            closest = df_num.sort_values("_dist").iloc[0]
            demo_match = {
                "configuration_id": int(closest["configuration_id"]) if pd.notna(closest.get("configuration_id")) else None,
                "components": str(closest.get("components", "")),
                "component_count": int(closest["component_count"]),
                "system_voltage_v": float(closest["system_voltage_v"]),
                "analysis_period_min": float(closest["analysis_period_min"]),
                "calculated_energy_mwh": round(float(closest["calculated_energy_mwh"]), 4),
                "anomaly_score": round(float(closest["anomaly_score"]), 6),
                "anomaly_status": str(closest["anomaly_status"]),
                "match_note": (
                    f"Closest match to demo session "
                    f"({demo_cc} component(s), {demo_v}V, {demo_t} min)"
                )
            }
            print(
                f"  Demo config match: config {demo_match['configuration_id']} -- "
                f"{demo_match['anomaly_status']} (score {demo_match['anomaly_score']})"
            )
    except Exception as e:
        print(f"  WARNING: Could not find demo config match: {e}")

    data["anomaly_detection"]["demo_config_match"] = demo_match

    print(f"  Total configurations: {total}")
    print(f"  Normal: {normal}  |  Anomalies: {anomalies}  ({data['anomaly_detection']['anomaly_percent']}%)")

    return data


# ============================================================
# LOAD OPTIMIZATION CSV
# ============================================================

def load_optimization_section(data):

    print("\nLoading optimization results...")

    try:
        df = pd.read_csv(OPTIMIZATION_CSV)
    except Exception as e:
        print(f"WARNING: Could not load optimization CSV: {e}")
        return data

    system_row = df[df["result_type"] == "SYSTEM"]
    if not system_row.empty:
        r = system_row.iloc[0]
        data["optimization"]["system_current_energy_mwh"] = round(float(r["current_energy_mwh"]), 6)
        data["optimization"]["system_optimized_energy_mwh"] = round(float(r["optimized_energy_mwh"]), 6)
        data["optimization"]["system_saving_mwh"] = round(float(r["energy_saving_mwh"]), 6)
        data["optimization"]["system_reduction_percent"] = round(float(r["reduction_percent"]), 2)

    # Reset lists before repopulating to avoid duplicates on re-run
    data["optimization"]["components"] = []
    data["optimization"]["top_options"] = []

    component_rows = df[df["result_type"] == "COMPONENT"]
    for _, r in component_rows.iterrows():
        data["optimization"]["components"].append({
            "component": str(r["component"]),
            "current_energy_mwh": round(float(r["current_energy_mwh"]), 6),
            "optimized_energy_mwh": round(float(r["optimized_energy_mwh"]), 6),
            "energy_saving_mwh": round(float(r["energy_saving_mwh"]), 6),
            "reduction_percent": round(float(r["reduction_percent"]), 2),
            "current_active_time_min": round(float(r["current_active_time_min"]), 2),
            "optimized_active_time_min": round(float(r["optimized_active_time_min"]), 2),
            "minimum_active_time_min": round(float(r["minimum_active_time_min"]), 2),
            "constraint_status": str(r["constraint_status"])
        })

    top_option_rows = df[df["result_type"].str.startswith("TOP_OPTION", na=False)]
    for _, r in top_option_rows.iterrows():
        data["optimization"]["top_options"].append({
            "rank": str(r["result_type"]),
            "component": str(r["component"]),
            "system_current_energy_mwh": round(float(r["current_energy_mwh"]), 6),
            "system_optimized_energy_mwh": round(float(r["optimized_energy_mwh"]), 6),
            "system_saving_mwh": round(float(r["energy_saving_mwh"]), 6),
            "system_reduction_percent": round(float(r["reduction_percent"]), 2),
            "optimized_active_time_min": round(float(r["optimized_active_time_min"]), 2),
            "minimum_active_time_min": round(float(r["minimum_active_time_min"]), 2),
            "constraint_status": str(r["constraint_status"])
        })

    print(f"  Components: {len(data['optimization']['components'])}")
    print(f"  System saving: {data['optimization']['system_saving_mwh']} mWh  ({data['optimization']['system_reduction_percent']}% reduction)")
    print(f"  Top options: {len(data['optimization']['top_options'])}")

    return data


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("  CIRCUITWISE AI -- export_results.py")
    print("=" * 60)

    # Load existing JSON if export_prediction.py already ran
    if OUTPUT_JSON.exists():
        with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["export_timestamp"] = datetime.now(timezone.utc).isoformat()
        print("\nUpdating existing circuitwise_results.json...")
    else:
        data = build_skeleton()
        print("\nCreating new circuitwise_results.json...")

    data = load_anomaly_section(data)
    data = load_optimization_section(data)

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nSaved: {OUTPUT_JSON}")
    print("\nexport_results.py complete.")


if __name__ == "__main__":
    main()
