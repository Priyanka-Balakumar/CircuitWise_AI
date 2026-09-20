import pandas as pd
import joblib
from pathlib import Path


# ============================================================
# CIRCUITWISE AI - V4.4
# Component-Aware Energy Calculator + Saved ML Prediction
# ============================================================

# ------------------------------------------------------------
# FILE PATHS
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

EXCEL_PATH = "D:\pri\ibm\projects\ibm ai project\CircuitWise_AI_Component_Power_Dataset.xlsx"
MODEL_PATH = "D:\pri\ibm\projects\ibm ai project\ml\models\power_prediction_model.pkl"


# ------------------------------------------------------------
# ML FEATURES
# IMPORTANT: These MUST match train.py exactly
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


# ------------------------------------------------------------
# LOAD COMPONENT DATASET
# ------------------------------------------------------------

print("=" * 65)
print("             CIRCUITWISE AI - V4.4")
print("     COMPONENT-AWARE POWER + ML PREDICTION ENGINE")
print("=" * 65)

try:
    df = pd.read_excel(EXCEL_PATH, sheet_name="Component Power Dataset")

    print("\nDataset loaded successfully.")
    print("Components available:", len(df))

except Exception as e:
    print("\nERROR: Could not load component dataset.")
    print("Reason:", e)
    raise SystemExit


# ------------------------------------------------------------
# LOAD SAVED ML MODEL
# ------------------------------------------------------------

try:
    model = joblib.load(MODEL_PATH)

    print("Saved ML model loaded successfully.")

except FileNotFoundError:
    print("\nERROR: ML model file was not found.")
    print("Expected location:")
    print(MODEL_PATH)
    print("\nRun train.py first to create the .pkl model.")
    raise SystemExit

except Exception as e:
    print("\nERROR: Could not load ML model.")
    print("Reason:", e)
    raise SystemExit


# ------------------------------------------------------------
# NORMALIZE MISSING VALUES
# ------------------------------------------------------------

def is_valid_number(value):
    """
    Returns True if value is a usable numeric value.
    Handles NaN, blank cells and text such as 'blank'.
    """
    if pd.isna(value):
        return False

    if isinstance(value, str):
        if value.strip().lower() in ["", "blank", "na", "n/a", "none", "-"]:
            return False

    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False


def get_current(row, mode):
    """
    Get current from the component dataset for a particular mode.

    Returns None if the dataset does not contain a defensible
    current value for that mode.
    """

    column_map = {
        "active": "active_current_ma",
        "idle": "idle_current_ma",
        "sleep": "sleep_current_ma",
        "peak": "peak_current_ma"
    }

    column = column_map[mode]

    if column not in row.index:
        return None

    value = row[column]

    if not is_valid_number(value):
        return None

    return float(value)


# ------------------------------------------------------------
# GET AVAILABLE MODES
# ------------------------------------------------------------

def get_available_modes(row):
    """
    Detect which operating modes actually have current data
    for a component.
    """

    modes = []

    for mode in ["active", "idle", "sleep", "peak"]:
        current = get_current(row, mode)

        if current is not None:
            modes.append(mode)

    return modes


# ------------------------------------------------------------
# DISPLAY COMPONENTS
# ------------------------------------------------------------

print("\nAVAILABLE COMPONENTS")
print("-" * 65)

for i, row in df.iterrows():
    print(
        f"{i + 1:2d}. "
        f"{row['component_name']} "
        f"({row['category']})"
    )


# ------------------------------------------------------------
# SELECT COMPONENTS
# ------------------------------------------------------------

print("\nSelect components one by one.")
print("Enter 0 when finished.")

selected_components = []

while True:

    try:
        choice = int(input("\nEnter component number: "))

    except ValueError:
        print("Please enter a valid number.")
        continue

    if choice == 0:
        break

    if choice < 1 or choice > len(df):
        print("Invalid component number.")
        continue

    row = df.iloc[choice - 1]

    selected_components.append(row)

    print(
        f"Added: {row['component_name']}"
    )


if len(selected_components) == 0:
    print("\nNo components selected.")
    raise SystemExit


# ------------------------------------------------------------
# SYSTEM INFORMATION
# ------------------------------------------------------------

print("\n" + "=" * 65)
print("SYSTEM CONFIGURATION")
print("=" * 65)

# System voltage
while True:

    try:
        system_voltage = float(
            input("Enter system voltage (V): ")
        )

        if system_voltage <= 0:
            print("Voltage must be greater than zero.")
            continue

        break

    except ValueError:
        print("Please enter a valid voltage.")


# Analysis period
while True:

    try:
        analysis_period = float(
            input("Enter analysis period (minutes): ")
        )

        if analysis_period <= 0:
            print("Analysis period must be greater than zero.")
            continue

        break

    except ValueError:
        print("Please enter a valid number.")


# ------------------------------------------------------------
# COMPONENT PROFILES
# ------------------------------------------------------------

print("\n" + "=" * 65)
print("COMPONENT OPERATING PROFILES")
print("=" * 65)

component_results = []


for row in selected_components:

    name = row["component_name"]

    available_modes = get_available_modes(row)

    print("\n" + "-" * 65)
    print(f"Component: {name}")

    print("Available modes:")

    for mode in available_modes:
        current = get_current(row, mode)
        print(f"  {mode.capitalize():8s}: {current} mA")

    print("\nEnter duration for each available mode.")
    print("Unavailable modes will not be used.")


    # Store durations for this component
    durations = {
        "active": 0.0,
        "idle": 0.0,
        "sleep": 0.0,
        "peak": 0.0
    }


    for mode in available_modes:

        while True:

            try:
                duration = float(
                    input(
                        f"{mode.capitalize()} duration "
                        f"(minutes): "
                    )
                )

                if duration < 0:
                    print("Duration cannot be negative.")
                    continue

                break

            except ValueError:
                print("Please enter a valid number.")

        durations[mode] = duration


    # --------------------------------------------------------
    # CALCULATE COMPONENT ENERGY
    # --------------------------------------------------------

    active_energy = 0.0
    idle_energy = 0.0
    sleep_energy = 0.0
    peak_energy = 0.0

    active_charge = 0.0
    idle_charge = 0.0
    sleep_charge = 0.0
    peak_charge = 0.0


    for mode in available_modes:

        current = get_current(row, mode)
        duration = durations[mode]

        if current is None:
            continue

        # Power:
        # P(W) = V(V) × I(A)
        #
        # Since current is in mA:
        # P(mW) = V × I(mA)

        power_mw = system_voltage * current

        # Energy:
        # E(mWh) = P(mW) × time(h)
        energy_mwh = power_mw * (duration / 60.0)

        # Charge:
        # Q(mAh) = I(mA) × time(h)
        charge_mah = current * (duration / 60.0)


        if mode == "active":
            active_energy += energy_mwh
            active_charge += charge_mah

        elif mode == "idle":
            idle_energy += energy_mwh
            idle_charge += charge_mah

        elif mode == "sleep":
            sleep_energy += energy_mwh
            sleep_charge += charge_mah

        elif mode == "peak":
            peak_energy += energy_mwh
            peak_charge += charge_mah


    total_energy = (
        active_energy
        + idle_energy
        + sleep_energy
        + peak_energy
    )

    total_charge = (
        active_charge
        + idle_charge
        + sleep_charge
        + peak_charge
    )


    # --------------------------------------------------------
    # COMPONENT RESULT
    # --------------------------------------------------------

    component_results.append({
        "name": name,
        "row": row,
        "available_modes": available_modes,
        "durations": durations,
        "active_energy": active_energy,
        "idle_energy": idle_energy,
        "sleep_energy": sleep_energy,
        "peak_energy": peak_energy,
        "total_energy": total_energy,
        "total_charge": total_charge
    })


# ============================================================
# ENGINEERING CALCULATION SUMMARY
# ============================================================

print("\n\n" + "=" * 65)
print("ENGINEERING POWER CALCULATION")
print("=" * 65)

system_total_energy = 0.0
system_total_charge = 0.0


for result in component_results:

    print("\n" + "-" * 65)
    print("Component:", result["name"])

    print(
        f"Active energy : "
        f"{result['active_energy']:.6f} mWh"
    )

    print(
        f"Idle energy   : "
        f"{result['idle_energy']:.6f} mWh"
    )

    print(
        f"Sleep energy  : "
        f"{result['sleep_energy']:.6f} mWh"
    )

    print(
        f"Peak energy   : "
        f"{result['peak_energy']:.6f} mWh"
    )

    print(
        f"Total energy  : "
        f"{result['total_energy']:.6f} mWh"
    )

    print(
        f"Charge used   : "
        f"{result['total_charge']:.6f} mAh"
    )

    system_total_energy += result["total_energy"]
    system_total_charge += result["total_charge"]


average_power_mw = (
    system_total_energy
    / (analysis_period / 60.0)
)


print("\n" + "=" * 65)
print("SYSTEM TOTAL")
print("=" * 65)

print(
    f"Total system energy : "
    f"{system_total_energy:.6f} mWh"
)

print(
    f"Average system power: "
    f"{average_power_mw:.6f} mW"
)

print(
    f"System charge used  : "
    f"{system_total_charge:.6f} mAh"
)


# ============================================================
# DAILY ENERGY
# ============================================================

daily_energy_mwh = (
    average_power_mw * 24
)

print(
    f"Estimated daily energy: "
    f"{daily_energy_mwh:.6f} mWh/day"
)


# ============================================================
# BUILD ML FEATURES
#
# These features must match the V4.4 training dataset.
# ============================================================

component_count = len(component_results)


# ------------------------------------------------------------
# Aggregate durations
#
# Average duration across selected components.
# ------------------------------------------------------------

active_durations = []
sleep_durations = []
peak_durations = []


for result in component_results:

    active_durations.append(
        result["durations"]["active"]
    )

    sleep_durations.append(
        result["durations"]["sleep"]
    )

    peak_durations.append(
        result["durations"]["peak"]
    )


active_duration = (
    sum(active_durations)
    / component_count
)

sleep_duration = (
    sum(sleep_durations)
    / component_count
)

peak_duration = (
    sum(peak_durations)
    / component_count
)


# ------------------------------------------------------------
# Aggregate current features
#
# Calculate time-weighted current for each mode.
#
# Only components that actually have that mode available
# contribute to that mode's current feature.
# ------------------------------------------------------------

active_current_values = []
sleep_current_values = []
peak_current_values = []


for result in component_results:

    row = result["row"]
    durations = result["durations"]


    # Active
    active_current = get_current(row, "active")

    if (
        active_current is not None
        and durations["active"] > 0
    ):
        active_current_values.append(
            active_current * durations["active"]
        )


    # Sleep
    sleep_current = get_current(row, "sleep")

    if (
        sleep_current is not None
        and durations["sleep"] > 0
    ):
        sleep_current_values.append(
            sleep_current * durations["sleep"]
        )


    # Peak
    peak_current = get_current(row, "peak")

    if (
        peak_current is not None
        and durations["peak"] > 0
    ):
        peak_current_values.append(
            peak_current * durations["peak"]
        )


# ------------------------------------------------------------
# Convert weighted currents to average currents
# ------------------------------------------------------------

active_total_duration = 0.0
sleep_total_duration = 0.0
peak_total_duration = 0.0


for result in component_results:

    durations = result["durations"]

    if get_current(result["row"], "active") is not None:
        active_total_duration += durations["active"]

    if get_current(result["row"], "sleep") is not None:
        sleep_total_duration += durations["sleep"]

    if get_current(result["row"], "peak") is not None:
        peak_total_duration += durations["peak"]


if active_total_duration > 0:

    avg_active_current = (
        sum(active_current_values)
        / active_total_duration
    )

else:

    avg_active_current = 0.0


if sleep_total_duration > 0:

    avg_sleep_current = (
        sum(sleep_current_values)
        / sleep_total_duration
    )

else:

    avg_sleep_current = 0.0


if peak_total_duration > 0:

    avg_peak_current = (
        sum(peak_current_values)
        / peak_total_duration
    )

else:

    avg_peak_current = 0.0


# ============================================================
# DISPLAY ML FEATURES
# ============================================================

print("\n" + "=" * 65)
print("ML FEATURES")
print("=" * 65)

print(
    f"Component count       : {component_count}"
)

print(
    f"System voltage        : {system_voltage:.4f} V"
)

print(
    f"Analysis period       : {analysis_period:.4f} min"
)

print(
    f"Active duration       : {active_duration:.4f} min"
)

print(
    f"Sleep duration        : {sleep_duration:.4f} min"
)

print(
    f"Peak duration         : {peak_duration:.4f} min"
)

print(
    f"Average active current: "
    f"{avg_active_current:.6f} mA"
)

print(
    f"Average sleep current : "
    f"{avg_sleep_current:.6f} mA"
)

print(
    f"Average peak current  : "
    f"{avg_peak_current:.6f} mA"
)


# ============================================================
# CREATE ML INPUT
# ============================================================

ml_input = pd.DataFrame([{
    "component_count": component_count,
    "system_voltage_v": system_voltage,
    "analysis_period_min": analysis_period,
    "active_duration_min": active_duration,
    "sleep_duration_min": sleep_duration,
    "peak_duration_min": peak_duration,
    "avg_active_current_ma": avg_active_current,
    "avg_sleep_current_ma": avg_sleep_current,
    "avg_peak_current_ma": avg_peak_current
}])


# Safety check
ml_input = ml_input[FEATURES]


# ============================================================
# ML PREDICTION
# ============================================================

try:

    prediction = model.predict(ml_input)

    predicted_energy = float(prediction[0])

except Exception as e:

    print("\nERROR during ML prediction.")
    print("Reason:", e)
    raise SystemExit


# ============================================================
# COMPARE ENGINEERING CALCULATION VS ML
# ============================================================

difference = (
    predicted_energy
    - system_total_energy
)

if system_total_energy != 0:

    difference_percent = (
        abs(difference)
        / system_total_energy
        * 100
    )

else:

    difference_percent = 0.0


print("\n" + "=" * 65)
print("ML PREDICTION")
print("=" * 65)

print(
    f"Engineering calculated energy : "
    f"{system_total_energy:.4f} mWh"
)

print(
    f"ML predicted energy           : "
    f"{predicted_energy:.4f} mWh"
)

print(
    f"Difference                    : "
    f"{difference:.4f} mWh"
)

print(
    f"Absolute difference           : "
    f"{difference_percent:.2f}%"
)


# ============================================================
# AI INTERPRETATION
# ============================================================

print("\n" + "=" * 65)
print("AI INTERPRETATION")
print("=" * 65)


if system_total_energy == 0:

    print(
        "The engineering calculation produced zero energy."
    )

elif difference_percent <= 10:

    print(
        "ML prediction is relatively close "
        "to the engineering calculation."
    )

elif difference_percent <= 25:

    print(
        "ML prediction shows a moderate difference "
        "from the engineering calculation."
    )

else:

    print(
        "ML prediction shows a significant difference "
        "from the engineering calculation."
    )


# ============================================================
# COMPONENT-LEVEL RECOMMENDATIONS
# ============================================================

print("\n" + "=" * 65)
print("POWER OPTIMIZATION RECOMMENDATIONS")
print("=" * 65)


recommendation_found = False


for result in component_results:

    row = result["row"]
    name = result["name"]
    durations = result["durations"]
    available_modes = result["available_modes"]


    # --------------------------------------------------------
    # Sleep recommendation
    # --------------------------------------------------------

    sleep_current = get_current(row, "sleep")
    active_current = get_current(row, "active")


    if (
        active_current is not None
        and sleep_current is None
        and durations["active"] > 0
    ):

        print(
            f"- {name}: no defensible sleep current "
            f"is available in the dataset. "
            f"Consider reducing active duty cycle "
            f"if the application allows it."
        )

        recommendation_found = True


    elif (
        active_current is not None
        and sleep_current is not None
        and durations["active"] > 0
        and durations["sleep"] == 0
    ):

        print(
            f"- {name}: active current is "
            f"{active_current:.4f} mA while sleep current is "
            f"{sleep_current:.6f} mA. "
            f"Consider sleep mode when functionality permits."
        )

        recommendation_found = True


    # --------------------------------------------------------
    # Active duty-cycle recommendation
    # --------------------------------------------------------

    if (
        durations["active"] > 0
        and durations["active"] >= analysis_period * 0.5
    ):

        print(
            f"- {name}: active for "
            f"{durations['active']:.2f} minutes. "
            f"Reducing active duty cycle may reduce energy."
        )

        recommendation_found = True


    # --------------------------------------------------------
    # Peak current recommendation
    # --------------------------------------------------------

    peak_current = get_current(row, "peak")

    if (
        peak_current is not None
        and peak_current > 100
        and durations["peak"] > 0
    ):

        print(
            f"- {name}: peak current is "
            f"{peak_current:.2f} mA. "
            f"Review peak-load events and power supply capacity."
        )

        recommendation_found = True


if not recommendation_found:

    print(
        "No major optimization recommendation was "
        "identified from the available dataset."
    )


# ============================================================
# FINAL STATUS
# ============================================================

print("\n" + "=" * 65)
print("CIRCUITWISE AI ANALYSIS COMPLETE")
print("=" * 65)

print(
    "\nNote: The ML model was trained using the "
    "V4.4 synthetic/calculated dataset."
)

print(
    "Hardware validation using actual measurements "
    "is required before treating predictions as "
    "real-world measurements."
)

print("\n")