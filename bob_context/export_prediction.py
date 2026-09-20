
# ============================================================
# CIRCUITWISE AI — BOB CONTEXT PREDICTION EXPORT
# export_prediction.py
#
# Non-interactive batch version of ml/predict.py.
# Reads bob_context/session_input.json, applies the identical
# engineering calculation (P = V x I_mA, E = P x duration/60)
# and ML inference (RandomForest .pkl), then writes the
# engineering_calculation and ml_prediction sections into
# bob_context/circuitwise_results.json.
#
# DOES NOT modify ml/predict.py or any other existing file.
# Uses the same formula and the same saved model.
# ============================================================

import json
import joblib
import pandas as pd

from datetime import datetime, timezone
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

SESSION_INPUT = Path(__file__).resolve().parent / "session_input.json"
OUTPUT_JSON = Path(__file__).resolve().parent / "circuitwise_results.json"
MODEL_PATH = BASE_DIR / "ml" / "models" / "power_prediction_model.pkl"


# ============================================================
# ML FEATURES — must match train.py and predict.py exactly
# ============================================================

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

# Interpretation bands (from predict.py)
BAND_CLOSE = 10.0      # <= 10%
BAND_MODERATE = 25.0   # <= 25%
# > 25% = significant deviation


# ============================================================
# HELPERS (mirrors logic in predict.py, no user prompts)
# ============================================================

def get_current(component, mode):
    """
    Return the current (mA) for the given mode from session_input.json data.
    Returns None if the value is null/missing (same semantics as predict.py).
    Null means no defensible datasheet value — NOT the same as zero.
    """
    key = f"{mode}_current_ma"
    value = component.get(key)
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def get_available_modes(component):
    """
    Return list of modes that have a non-null current value.
    Only modes with a real current value are available.
    """
    modes = []
    for mode in ("active", "idle", "sleep", "peak"):
        current = get_current(component, mode)
        if current is not None:
            modes.append(mode)
    return modes


def calculate_component_energy(component, system_voltage):
    """
    Apply P = V x I_mA (mW) and E = P x (duration_min / 60) (mWh)
    for each available mode. Mirrors the per-component loop in predict.py.
    """
    available_modes = get_available_modes(component)

    mode_results = {}
    total_energy = 0.0
    total_charge = 0.0

    for mode in available_modes:
        current = get_current(component, mode)
        duration = float(component.get(f"{mode}_duration_min", 0.0) or 0.0)

        power_mw = system_voltage * current
        energy_mwh = power_mw * (duration / 60.0)
        charge_mah = current * (duration / 60.0)

        mode_results[mode] = {
            "current_ma": current,
            "duration_min": duration,
            "power_mw": round(power_mw, 6),
            "energy_mwh": round(energy_mwh, 6),
            "charge_mah": round(charge_mah, 6)
        }
        total_energy += energy_mwh
        total_charge += charge_mah

    return {
        "name": component["name"],
        "component_id": component.get("component_id", ""),
        "source": component.get("source", ""),
        "available_modes": available_modes,
        "mode_results": mode_results,
        "total_energy_mwh": round(total_energy, 6),
        "total_charge_mah": round(total_charge, 6),
        "durations": {
            mode: float(component.get(f"{mode}_duration_min", 0.0) or 0.0)
            for mode in ("active", "idle", "sleep", "peak")
        }
    }


def build_ml_features(component_results, system_voltage, analysis_period):
    """
    Aggregate per-component results into the 9 ML features.
    Mirrors the aggregation block in predict.py (lines 500–660).
    """
    component_count = len(component_results)

    # --- Average durations ---
    active_duration = sum(r["durations"]["active"] for r in component_results) / component_count
    sleep_duration = sum(r["durations"]["sleep"] for r in component_results) / component_count
    peak_duration = sum(r["durations"]["peak"] for r in component_results) / component_count

    # --- Time-weighted average currents ---
    active_current_values = []
    sleep_current_values = []
    peak_current_values = []

    active_total_duration = 0.0
    sleep_total_duration = 0.0
    peak_total_duration = 0.0

    for r in component_results:
        durations = r["durations"]
        modes = r["available_modes"]

        if "active" in modes:
            c = r["mode_results"]["active"]["current_ma"]
            d = durations["active"]
            if d > 0:
                active_current_values.append(c * d)
            active_total_duration += d

        if "sleep" in modes:
            c = r["mode_results"]["sleep"]["current_ma"]
            d = durations["sleep"]
            if d > 0:
                sleep_current_values.append(c * d)
            sleep_total_duration += d

        if "peak" in modes:
            c = r["mode_results"]["peak"]["current_ma"]
            d = durations["peak"]
            if d > 0:
                peak_current_values.append(c * d)
            peak_total_duration += d

    avg_active_current = sum(active_current_values) / active_total_duration if active_total_duration > 0 else 0.0
    avg_sleep_current = sum(sleep_current_values) / sleep_total_duration if sleep_total_duration > 0 else 0.0
    avg_peak_current = sum(peak_current_values) / peak_total_duration if peak_total_duration > 0 else 0.0

    return {
        "component_count": component_count,
        "system_voltage_v": system_voltage,
        "analysis_period_min": analysis_period,
        "active_duration_min": round(active_duration, 6),
        "sleep_duration_min": round(sleep_duration, 6),
        "peak_duration_min": round(peak_duration, 6),
        "avg_active_current_ma": round(avg_active_current, 6),
        "avg_sleep_current_ma": round(avg_sleep_current, 6),
        "avg_peak_current_ma": round(avg_peak_current, 6)
    }


def build_recommendations(component_results, analysis_period):
    """
    Generate text recommendations mirroring predict.py lines 841-937.
    """
    recs = []
    for r in component_results:
        name = r["name"]
        modes = r["available_modes"]
        durations = r["durations"]

        active_current = r["mode_results"].get("active", {}).get("current_ma")
        sleep_current = r["mode_results"].get("sleep", {}).get("current_ma")
        peak_current = r["mode_results"].get("peak", {}).get("current_ma")

        if (
            active_current is not None
            and "sleep" not in modes
            and durations["active"] > 0
        ):
            recs.append(
                f"{name}: no defensible sleep current is available in the dataset. "
                f"Consider reducing active duty cycle if the application allows it."
            )

        elif (
            active_current is not None
            and sleep_current is not None
            and durations["active"] > 0
            and durations["sleep"] == 0
        ):
            recs.append(
                f"{name}: active current is {active_current:.4f} mA while sleep current is "
                f"{sleep_current:.6f} mA. Consider sleep mode when functionality permits."
            )

        if durations["active"] > 0 and durations["active"] >= analysis_period * 0.5:
            recs.append(
                f"{name}: active for {durations['active']:.2f} minutes. "
                f"Reducing active duty cycle may reduce energy."
            )

        if peak_current is not None and peak_current > 100 and durations["peak"] > 0:
            recs.append(
                f"{name}: peak current is {peak_current:.2f} mA. "
                f"Review peak-load events and power supply capacity."
            )

    if not recs:
        recs.append(
            "No major optimization recommendation was identified from the available dataset."
        )
    return recs


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("  CIRCUITWISE AI -- export_prediction.py")
    print("=" * 60)


    # --------------------------------------------------------
    # 1. LOAD SESSION INPUT
    # --------------------------------------------------------

    print("\nLoading session input...")

    try:
        with open(SESSION_INPUT, "r", encoding="utf-8") as f:
            session = json.load(f)
    except Exception as e:
        print(f"ERROR: Could not load session_input.json: {e}")
        raise SystemExit

    system_voltage = float(session["system_voltage_v"])
    analysis_period = float(session["analysis_period_min"])
    session_name = session.get("session_name", "CircuitWise AI Session")
    components_input = session["components"]

    print(f"  Session: {session_name}")
    print(f"  System voltage: {system_voltage} V")
    print(f"  Analysis period: {analysis_period} min")
    print(f"  Components: {len(components_input)}")


    # --------------------------------------------------------
    # 2. LOAD ML MODEL
    # --------------------------------------------------------

    print("\nLoading ML model...")

    try:
        model = joblib.load(MODEL_PATH)
    except Exception as e:
        print(f"ERROR: Could not load model from {MODEL_PATH}: {e}")
        raise SystemExit

    print(f"  Model loaded: {MODEL_PATH.name}")


    # --------------------------------------------------------
    # 3. ENGINEERING CALCULATIONS
    # --------------------------------------------------------

    print("\nRunning engineering calculations (P = V x I_mA; E = P x t/60)...")

    component_results = []
    for comp in components_input:
        result = calculate_component_energy(comp, system_voltage)
        component_results.append(result)
        print(
            f"  {result['name']:30s}  "
            f"{result['total_energy_mwh']:.4f} mWh  "
            f"(modes: {', '.join(result['available_modes'])})"
        )

    system_total_energy = sum(r["total_energy_mwh"] for r in component_results)
    print(f"\n  System total energy: {system_total_energy:.4f} mWh")


    # --------------------------------------------------------
    # 4. BUILD ML FEATURE VECTOR
    # --------------------------------------------------------

    features = build_ml_features(component_results, system_voltage, analysis_period)

    print("\nML feature vector:")
    for k, v in features.items():
        print(f"  {k}: {v}")


    # --------------------------------------------------------
    # 5. ML PREDICTION
    # --------------------------------------------------------

    print("\nRunning ML prediction...")

    ml_input = pd.DataFrame([features])[FEATURES]

    try:
        prediction = model.predict(ml_input)
        predicted_energy = float(prediction[0])
    except Exception as e:
        print(f"ERROR during ML prediction: {e}")
        raise SystemExit

    difference = predicted_energy - system_total_energy
    difference_percent = (
        abs(difference) / system_total_energy * 100
        if system_total_energy != 0 else 0.0
    )

    if system_total_energy == 0:
        interpretation_band = "zero_calculated_energy"
    elif difference_percent <= BAND_CLOSE:
        interpretation_band = "close_agreement"
    elif difference_percent <= BAND_MODERATE:
        interpretation_band = "moderate_deviation"
    else:
        interpretation_band = "significant_deviation"

    print(f"  Calculated: {system_total_energy:.4f} mWh")
    print(f"  Predicted:  {predicted_energy:.4f} mWh")
    print(f"  Difference: {difference:.4f} mWh  ({difference_percent:.2f}%)")
    print(f"  Band:       {interpretation_band}")


    # --------------------------------------------------------
    # 6. RECOMMENDATIONS
    # --------------------------------------------------------

    recommendations = build_recommendations(component_results, analysis_period)


    # --------------------------------------------------------
    # 7. LOAD / CREATE JSON AND UPDATE SECTIONS
    # --------------------------------------------------------

    if OUTPUT_JSON.exists():
        with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        from export_results import build_skeleton
        data = build_skeleton()

    data["export_timestamp"] = datetime.now(timezone.utc).isoformat()
    data["session_name"] = session_name

    # Engineering calculation block
    data["engineering_calculation"] = {
        "session_name": session_name,
        "system_voltage_v": system_voltage,
        "analysis_period_min": analysis_period,
        "component_count": len(component_results),
        "system_total_energy_mwh": round(system_total_energy, 6),
        "calculation_method": "P = V x I_mA (mW);  E = P x (duration_min / 60) (mWh)",
        "components": [
            {
                "name": r["name"],
                "component_id": r["component_id"],
                "source": r["source"],
                "available_modes": r["available_modes"],
                "total_energy_mwh": r["total_energy_mwh"],
                "total_charge_mah": r["total_charge_mah"],
                "mode_detail": {
                    mode: {
                        "current_ma": r["mode_results"][mode]["current_ma"],
                        "duration_min": r["mode_results"][mode]["duration_min"],
                        "energy_mwh": r["mode_results"][mode]["energy_mwh"]
                    }
                    for mode in r["available_modes"]
                }
            }
            for r in component_results
        ],
        "recommendations": recommendations
    }

    # ML prediction block
    data["ml_prediction"] = {
        "predicted_energy_mwh": round(predicted_energy, 6),
        "calculated_energy_mwh": round(system_total_energy, 6),
        "difference_from_calculated_mwh": round(difference, 6),
        "difference_percent": round(difference_percent, 4),
        "interpretation_band": interpretation_band,
        "features_used": FEATURES,
        "feature_values": features,
        "model": "RandomForestRegressor(n_estimators=200, random_state=42)",
        "note": (
            "Prediction is based on a model trained on synthetic/calculated data "
            "(V4.4 dataset). It is NOT a hardware measurement. "
            "The difference between calculated and predicted reflects model error "
            "on synthetic training data — not a measured physical discrepancy."
        )
    }

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nSaved: {OUTPUT_JSON}")
    print("\nexport_prediction.py complete.")


if __name__ == "__main__":
    main()
