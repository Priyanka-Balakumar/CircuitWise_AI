import pandas as pd
# ============================================================
# CIRCUITWISE AI - V3.1
# IoT Energy Profile Analyzer
# Automatic handling of unavailable operating modes
# ============================================================
DATASET_PATH = "D:\pri\ibm\projects\ibm ai project\CircuitWise_AI_Component_Power_Dataset.xlsx"
SHEET_NAME = "Component Power Dataset"
# ------------------------------------------------------------
# LOAD DATASET
# ------------------------------------------------------------
def load_dataset():
    try:
        df = pd.read_excel(
            DATASET_PATH,
            sheet_name=SHEET_NAME,
            engine="openpyxl"
        )
        # Normalize text values
        df = df.replace(
            [
                "blank",
                "Blank",
                "BLANK",
                "N/A",
                "n/a",
                "NA",
                "None",
                "none",
                "null",
                "-",
                ""
            ],
            pd.NA
        )

        print("\nDataset loaded successfully.")
        print(f"Components available: {len(df)}")
        return df
    except Exception as e:
        print("\nERROR: Could not load dataset.")
        print(e)
        return None
# ------------------------------------------------------------
# DISPLAY COMPONENTS
# ------------------------------------------------------------
def display_components(df):

    print("\n" + "=" * 70)
    print("AVAILABLE COMPONENTS")
    print("=" * 70)

    for index, row in df.iterrows():

        print(
            f"{index + 1:2d}. "
            f"{row['component_name']:<30} | "
            f"{row['category']}"
        )


# ------------------------------------------------------------
# GET CURRENT FOR A MODE
# ------------------------------------------------------------

def get_current(row, mode):

    column_map = {
        "active": "active_current_ma",
        "idle": "idle_current_ma",
        "sleep": "sleep_current_ma",
        "peak": "peak_current_ma"
    }

    column = column_map[mode]

    value = row[column]

    # Missing value
    if pd.isna(value):
        return None

    try:

        value = float(value)

        return value

    except (ValueError, TypeError):

        return None


# ------------------------------------------------------------
# GET VOLTAGE
# ------------------------------------------------------------

def get_voltage(row):

    value = row["supply_voltage_typ_v"]

    if not pd.isna(value):

        try:
            return float(value)

        except (ValueError, TypeError):
            pass

    # If typical voltage unavailable
    while True:

        try:

            voltage = float(
                input(
                    f"\nEnter operating voltage for "
                    f"{row['component_name']} (V): "
                )
            )

            if voltage > 0:
                return voltage

            print("Voltage must be greater than 0.")

        except ValueError:

            print("Please enter a valid number.")


# ------------------------------------------------------------
# CALCULATE POWER
# ------------------------------------------------------------

def calculate_power(voltage, current_ma):

    current_a = current_ma / 1000

    power_w = voltage * current_a

    power_mw = power_w * 1000

    return power_mw


# ------------------------------------------------------------
# CALCULATE ENERGY
# ------------------------------------------------------------

def calculate_energy(power_mw, duration_minutes):

    duration_hours = duration_minutes / 60

    energy_mwh = power_mw * duration_hours

    return energy_mwh


# ------------------------------------------------------------
# GET AVAILABLE MODES
# ------------------------------------------------------------

def get_available_modes(row):

    modes = [
        "active",
        "idle",
        "sleep",
        "peak"
    ]

    available_modes = []

    for mode in modes:

        current = get_current(row, mode)

        if current is not None:

            available_modes.append(mode)

    return available_modes


# ------------------------------------------------------------
# DISPLAY MODE AVAILABILITY
# ------------------------------------------------------------

def display_mode_availability(row):

    print("\n" + "-" * 60)
    print(f"POWER MODE AVAILABILITY: {row['component_name']}")
    print("-" * 60)

    modes = [
        "active",
        "idle",
        "sleep",
        "peak"
    ]

    for mode in modes:

        current = get_current(row, mode)

        if current is not None:

            print(
                f"✓ {mode.upper():<8} "
                f"{current:.5f} mA"
            )

        else:

            print(
                f"✗ {mode.upper():<8} "
                f"Current data unavailable"
            )


# ------------------------------------------------------------
# GET MODE DURATION
# ------------------------------------------------------------

def get_duration(mode, remaining_minutes):

    while True:

        try:

            duration = float(
                input(
                    f"Enter {mode.upper()} duration "
                    f"(minutes, remaining {remaining_minutes:.2f}): "
                )
            )

            if duration < 0:

                print("Duration cannot be negative.")
                continue

            if duration > remaining_minutes:

                print(
                    f"Duration cannot exceed "
                    f"{remaining_minutes:.2f} minutes."
                )
                continue

            return duration

        except ValueError:

            print("Please enter a valid number.")


# ------------------------------------------------------------
# MAIN PROGRAM
# ------------------------------------------------------------

def main():

    print("\n")
    print("=" * 70)
    print("          CIRCUITWISE AI - V3.1")
    print("          IoT ENERGY PROFILE ANALYZER")
    print("=" * 70)

    # Load dataset

    df = load_dataset()

    if df is None:
        return

    # Display components

    display_components(df)

    # --------------------------------------------------------
    # SELECT NUMBER OF COMPONENTS
    # --------------------------------------------------------

    while True:

        try:

            number_of_components = int(
                input("\nEnter number of components: ")
            )

            if (
                number_of_components >= 1
                and number_of_components <= len(df)
            ):

                break

            print(
                f"Enter a number between 1 and {len(df)}."
            )

        except ValueError:

            print("Please enter a valid number.")

    # --------------------------------------------------------
    # SELECT COMPONENTS
    # --------------------------------------------------------

    selected_components = []

    for i in range(number_of_components):

        while True:

            try:

                component_number = int(
                    input(
                        f"\nEnter component number "
                        f"{i + 1}: "
                    )
                )

                if (
                    component_number >= 1
                    and component_number <= len(df)
                ):

                    row = df.iloc[component_number - 1]

                    selected_components.append(row)

                    break

                print(
                    f"Enter a number between 1 and {len(df)}."
                )

            except ValueError:

                print("Please enter a valid number.")

    # --------------------------------------------------------
    # ANALYSIS PERIOD
    # --------------------------------------------------------

    while True:

        try:

            analysis_minutes = float(
                input(
                    "\nEnter analysis period "
                    "(minutes): "
                )
            )

            if analysis_minutes > 0:
                break

            print("Analysis period must be greater than 0.")

        except ValueError:

            print("Please enter a valid number.")

    # --------------------------------------------------------
    # RESULTS STORAGE
    # --------------------------------------------------------

    all_results = []

    total_system_energy = 0

    print("\n")
    print("=" * 70)
    print("MODE AVAILABILITY CHECK")
    print("=" * 70)

    # --------------------------------------------------------
    # PROCESS EACH COMPONENT
    # --------------------------------------------------------

    for row in selected_components:

        component_name = row["component_name"]

        voltage = get_voltage(row)

        # Show available modes

        display_mode_availability(row)

        available_modes = get_available_modes(row)

        print(
            f"\nAvailable modes for "
            f"{component_name}: "
            f"{', '.join(available_modes).upper()}"
        )

        remaining_minutes = analysis_minutes

        component_energy = 0

        component_results = []

        print("\nEnter operating profile:")

        # ----------------------------------------------------
        # ASK ONLY AVAILABLE MODES
        # ----------------------------------------------------

        for index, mode in enumerate(available_modes):

            # Last available mode automatically gets
            # remaining time if desired.

            if index == len(available_modes) - 1:

                print(
                    f"\nRemaining time for "
                    f"{mode.upper()}: "
                    f"{remaining_minutes:.2f} minutes"
                )

                use_remaining = input(
                    f"Use all remaining time for "
                    f"{mode.upper()}? (y/n): "
                ).lower()

                if use_remaining == "y":

                    duration = remaining_minutes

                else:

                    duration = get_duration(
                        mode,
                        remaining_minutes
                    )

            else:

                duration = get_duration(
                    mode,
                    remaining_minutes
                )

            # Update remaining time

            remaining_minutes -= duration

            # Get current

            current_ma = get_current(
                row,
                mode
            )

            # Calculate power

            power_mw = calculate_power(
                voltage,
                current_ma
            )

            # Calculate energy

            energy_mwh = calculate_energy(
                power_mw,
                duration
            )

            component_energy += energy_mwh

            component_results.append(
                {
                    "component": component_name,
                    "mode": mode.upper(),
                    "voltage": voltage,
                    "current_ma": current_ma,
                    "power_mw": power_mw,
                    "duration_min": duration,
                    "energy_mwh": energy_mwh
                }
            )

        # ----------------------------------------------------
        # CHECK REMAINING TIME
        # ----------------------------------------------------

        if remaining_minutes > 0.001:

            print(
                f"\nWARNING: "
                f"{remaining_minutes:.2f} minutes "
                f"were not assigned to a mode."
            )

        print("\n" + "-" * 60)
        print(f"ENERGY PROFILE: {component_name}")
        print("-" * 60)

        for result in component_results:

            print(
                f"{result['mode']:<8} | "
                f"{result['current_ma']:.5f} mA | "
                f"{result['power_mw']:.3f} mW | "
                f"{result['duration_min']:.2f} min | "
                f"{result['energy_mwh']:.3f} mWh"
            )

        print(
            f"\nTotal energy for {component_name}: "
            f"{component_energy:.3f} mWh"
        )

        total_system_energy += component_energy

        all_results.extend(component_results)

    # --------------------------------------------------------
    # SYSTEM RESULTS
    # --------------------------------------------------------

    analysis_hours = analysis_minutes / 60

    average_system_power = (
        total_system_energy / analysis_hours
    )

    daily_energy = (
        total_system_energy
        * (24 / analysis_hours)
    )

    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("CIRCUITWISE AI V3.1 ANALYSIS RESULT")
    print("=" * 70)

    print(
        f"\nAnalysis period:       "
        f"{analysis_minutes:.2f} minutes"
    )

    print(
        f"Total system energy:   "
        f"{total_system_energy:.3f} mWh"
    )

    print(
        f"Average system power:  "
        f"{average_system_power:.3f} mW"
    )

    print(
        f"Estimated daily energy:"
        f" {daily_energy:.3f} mWh/day"
    )

    # --------------------------------------------------------
    # BATTERY ESTIMATION
    # --------------------------------------------------------

    battery_choice = input(
        "\nDo you want to estimate battery life? (y/n): "
    ).lower()

    if battery_choice == "y":

        while True:

            try:

                battery_voltage = float(
                    input(
                        "Enter battery voltage (V): "
                    )
                )

                if battery_voltage > 0:
                    break

                print("Voltage must be greater than 0.")

            except ValueError:

                print("Please enter a valid number.")

        while True:

            try:

                battery_capacity = float(
                    input(
                        "Enter battery capacity (mAh): "
                    )
                )

                if battery_capacity > 0:
                    break

                print(
                    "Battery capacity must be "
                    "greater than 0."
                )

            except ValueError:

                print("Please enter a valid number.")

        # Battery energy

        battery_energy_mwh = (
            battery_voltage
            * battery_capacity
        )

        # Theoretical battery life

        battery_life_hours = (
            battery_energy_mwh
            / average_system_power
        )

        battery_life_days = (
            battery_life_hours / 24
        )

        print("\n" + "-" * 60)
        print("BATTERY ESTIMATION RESULT")
        print("-" * 60)

        print(
            f"Battery voltage:       "
            f"{battery_voltage:.2f} V"
        )

        print(
            f"Battery capacity:      "
            f"{battery_capacity:.0f} mAh"
        )

        print(
            f"Average system power:  "
            f"{average_system_power:.3f} mW"
        )

        print(
            f"Estimated battery life:"
            f" {battery_life_hours:.2f} hours"
        )

        print(
            f"Estimated battery life:"
            f" {battery_life_days:.2f} days"
        )

        print(
            "\nNOTE: This is a theoretical estimate."
        )

        print(
            "Real battery life depends on regulator "
            "losses, battery characteristics, "
            "temperature, load behavior, and "
            "other hardware factors."
        )

    # --------------------------------------------------------
    # COMPLETE
    # --------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("CIRCUITWISE AI V3.1 ANALYSIS COMPLETE")
    print("=" * 70)


# ------------------------------------------------------------
# PROGRAM START
# ------------------------------------------------------------

if __name__ == "__main__":
    main()