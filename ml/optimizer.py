from pathlib import Path
import pandas as pd


# ============================================================
# CIRCUITWISE AI - INTELLIGENT CONSTRAINT-AWARE OPTIMIZER
# WITH CSV RESULT SAVING
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = "D:\pri\ibm\projects\ibm ai project\CircuitWise_AI_Component_Power_Dataset.xlsx"

OUTPUT_DIR = BASE_DIR / "data"

OUTPUT_PATH = (
    OUTPUT_DIR
    / "CircuitWise_AI_Optimization_Results.csv"
)


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# LOAD DATASET
# ============================================================

try:

    df = pd.read_excel(
        DATA_PATH,
        sheet_name="Component Power Dataset"
    )

    print("\nDataset loaded successfully.")
    print(
        f"Components available: {len(df)}"
    )

except Exception as e:

    print(
        "\nERROR: Could not load component dataset."
    )

    print(e)

    raise SystemExit


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_number(value):

    if pd.isna(value):
        return None

    if isinstance(value, str):

        value = value.strip().lower()

        if value in [
            "",
            "blank",
            "na",
            "n/a",
            "none",
            "-"
        ]:
            return None

    try:

        return float(value)

    except (ValueError, TypeError):

        return None


def get_current(row, mode):

    columns = {

        "active":
            "active_current_ma",

        "idle":
            "idle_current_ma",

        "sleep":
            "sleep_current_ma",

        "peak":
            "peak_current_ma"
    }

    return clean_number(
        row[columns[mode]]
    )


def calculate_energy(
    voltage,
    current_ma,
    duration_min
):

    if (
        current_ma is None
        or duration_min <= 0
    ):
        return 0.0

    power_mw = (
        voltage * current_ma
    )

    energy_mwh = (
        power_mw
        * (duration_min / 60)
    )

    return energy_mwh


def available_modes(row):

    modes = []

    for mode in [
        "active",
        "idle",
        "sleep",
        "peak"
    ]:

        current = get_current(
            row,
            mode
        )

        if current is not None:

            modes.append(mode)

    return modes


def calculate_profiles_energy(
    component,
    profiles
):

    total = 0.0

    for profile in profiles:

        total += calculate_energy(
            component["voltage"],
            profile["current"],
            profile["duration"]
        )

    return total


# ============================================================
# HEADER
# ============================================================

print("\n" + "=" * 65)

print(
    "CIRCUITWISE AI - "
    "INTELLIGENT OPTIMIZER"
)

print("=" * 65)


# ============================================================
# COMPONENT SELECTION
# ============================================================

print("\nAvailable Components:\n")

for index, row in df.iterrows():

    print(
        f"{index + 1:2d}. "
        f"{row['component_name']} "
        f"({row['category']})"
    )


while True:

    try:

        selection = input(
            "\nEnter component numbers "
            "separated by commas: "
        )

        selected_indices = [
            int(x.strip()) - 1
            for x in selection.split(",")
        ]

        if len(selected_indices) == 0:

            raise ValueError

        if any(
            i < 0 or i >= len(df)
            for i in selected_indices
        ):

            raise ValueError

        break

    except ValueError:

        print(
            "Invalid selection. "
            "Example: 1,5"
        )


# ============================================================
# SYSTEM SETTINGS
# ============================================================

while True:

    try:

        system_voltage = float(
            input(
                "\nEnter system voltage (V): "
            )
        )

        if system_voltage <= 0:

            raise ValueError

        break

    except ValueError:

        print(
            "Enter a valid positive voltage."
        )


while True:

    try:

        analysis_period = float(
            input(
                "Enter analysis period "
                "(minutes): "
            )
        )

        if analysis_period <= 0:

            raise ValueError

        break

    except ValueError:

        print(
            "Enter a valid positive duration."
        )


# ============================================================
# COMPONENT PROFILES
# ============================================================

components = []

print("\n" + "=" * 65)

print(
    "OPERATING PROFILES"
)

print("=" * 65)


for index in selected_indices:

    row = df.iloc[index]

    name = row["component_name"]

    modes = available_modes(row)

    print("\n" + "-" * 65)

    print(
        f"Component: {name}"
    )

    print("\nAvailable modes:")

    for mode in modes:

        current = get_current(
            row,
            mode
        )

        print(
            f"  {mode.capitalize():6s}: "
            f"{current:.6f} mA"
        )


    profiles = []

    remaining_time = analysis_period

    active_duration = 0.0


    # --------------------------------------------------------
    # ACTIVE MODE
    # --------------------------------------------------------

    if "active" in modes:

        while True:

            try:

                active_duration = float(
                    input(
                        f"\n{name} - "
                        "Active duration (min): "
                    )
                )

                if (
                    active_duration < 0
                    or active_duration > analysis_period
                ):

                    raise ValueError

                break

            except ValueError:

                print(
                    "Enter a duration between "
                    "0 and the analysis period."
                )


        if active_duration > 0:

            profiles.append({

                "mode":
                    "active",

                "current":
                    get_current(
                        row,
                        "active"
                    ),

                "duration":
                    active_duration
            })

        remaining_time -= active_duration


    # --------------------------------------------------------
    # SLEEP MODE
    # --------------------------------------------------------

    if (
        "sleep" in modes
        and remaining_time > 0
    ):

        while True:

            try:

                sleep_duration = float(
                    input(
                        f"{name} - "
                        "Sleep duration "
                        f"(remaining "
                        f"{remaining_time:.2f} min): "
                    )
                )

                if (
                    sleep_duration < 0
                    or sleep_duration > remaining_time
                ):

                    raise ValueError

                break

            except ValueError:

                print(
                    "Enter a valid sleep duration."
                )


        if sleep_duration > 0:

            profiles.append({

                "mode":
                    "sleep",

                "current":
                    get_current(
                        row,
                        "sleep"
                    ),

                "duration":
                    sleep_duration
            })

        remaining_time -= sleep_duration


    # --------------------------------------------------------
    # PEAK MODE
    # --------------------------------------------------------

    if (
        "peak" in modes
        and remaining_time > 0
    ):

        while True:

            try:

                peak_duration = float(
                    input(
                        f"{name} - "
                        "Peak duration "
                        f"(remaining "
                        f"{remaining_time:.2f} min): "
                    )
                )

                if (
                    peak_duration < 0
                    or peak_duration > remaining_time
                ):

                    raise ValueError

                break

            except ValueError:

                print(
                    "Enter a valid peak duration."
                )


        if peak_duration > 0:

            profiles.append({

                "mode":
                    "peak",

                "current":
                    get_current(
                        row,
                        "peak"
                    ),

                "duration":
                    peak_duration
            })

        remaining_time -= peak_duration


    # --------------------------------------------------------
    # IDLE MODE
    # --------------------------------------------------------

    if (
        "idle" in modes
        and remaining_time > 0
    ):

        profiles.append({

            "mode":
                "idle",

            "current":
                get_current(
                    row,
                    "idle"
                ),

            "duration":
                remaining_time
        })

        remaining_time = 0


    # --------------------------------------------------------
    # FUNCTIONALITY CONSTRAINT
    # --------------------------------------------------------

    print(
        "\nFunctionality Constraint"
    )


    if active_duration > 0:

        while True:

            try:

                minimum_active = float(
                    input(
                        f"Minimum required "
                        f"active time for "
                        f"{name} (min): "
                    )
                )

                if (
                    minimum_active < 0
                    or minimum_active > active_duration
                ):

                    raise ValueError

                break

            except ValueError:

                print(
                    "Minimum active time must "
                    "be between 0 and current "
                    "active time."
                )

    else:

        minimum_active = 0.0


    components.append({

        "name":
            name,

        "voltage":
            system_voltage,

        "profiles":
            profiles,

        "active_duration":
            active_duration,

        "minimum_active":
            minimum_active
    })


# ============================================================
# CURRENT DESIGN
# ============================================================

print("\n" + "=" * 65)

print(
    "CURRENT DESIGN"
)

print("=" * 65)


total_current_energy = 0.0


for component in components:

    energy = calculate_profiles_energy(
        component,
        component["profiles"]
    )

    component["current_energy"] = energy

    total_current_energy += energy

    print(
        f"{component['name']}: "
        f"{energy:.6f} mWh"
    )


print(
    f"\nTOTAL SYSTEM ENERGY: "
    f"{total_current_energy:.6f} mWh"
)


# ============================================================
# INTELLIGENT OPTIMIZATION SEARCH
# ============================================================

print("\n" + "=" * 65)

print(
    "SEARCHING FOR LOWEST-ENERGY "
    "FEASIBLE DESIGN"
)

print("=" * 65)


all_options = []


for component in components:

    name = component["name"]

    current_energy = (
        component["current_energy"]
    )

    active_duration = (
        component["active_duration"]
    )

    minimum_active = (
        component["minimum_active"]
    )


    if active_duration <= 0:

        continue


    # --------------------------------------------------------
    # TEST ACTIVE-TIME REDUCTIONS
    # 0%, 5%, 10%, ... 100%
    # --------------------------------------------------------

    for reduction_percent in range(
        0,
        101,
        5
    ):

        new_active = (
            active_duration
            * (
                1
                - reduction_percent / 100
            )
        )


        # ----------------------------------------------------
        # FUNCTIONALITY CONSTRAINT
        # ----------------------------------------------------

        if new_active < minimum_active:

            continue


        # ----------------------------------------------------
        # DETERMINE REDUCED ACTIVE TIME
        # ----------------------------------------------------

        active_reduction_time = (
            active_duration
            - new_active
        )


        # ----------------------------------------------------
        # CREATE NEW PROFILES
        # ----------------------------------------------------

        new_profiles = []


        for profile in component["profiles"]:

            # ACTIVE
            if profile["mode"] == "active":

                new_profiles.append({

                    "mode":
                        "active",

                    "current":
                        profile["current"],

                    "duration":
                        new_active
                })


            # SLEEP
            elif (
                profile["mode"] == "sleep"
                and active_reduction_time > 0
            ):

                new_profiles.append({

                    "mode":
                        "sleep",

                    "current":
                        profile["current"],

                    "duration":
                        (
                            profile["duration"]
                            + active_reduction_time
                        )
                })


            # OTHER MODES
            else:

                new_profiles.append(
                    profile.copy()
                )


        # ----------------------------------------------------
        # CALCULATE OPTIMIZED COMPONENT ENERGY
        # ----------------------------------------------------

        optimized_component_energy = (
            calculate_profiles_energy(
                component,
                new_profiles
            )
        )


        # ----------------------------------------------------
        # ENERGY SAVING
        # ----------------------------------------------------

        saving = (
            current_energy
            - optimized_component_energy
        )


        # ----------------------------------------------------
        # SYSTEM ENERGY
        # ----------------------------------------------------

        system_energy = (
            total_current_energy
            - saving
        )


        # ----------------------------------------------------
        # SYSTEM REDUCTION
        # ----------------------------------------------------

        system_reduction = (

            saving
            / total_current_energy
            * 100

        ) if total_current_energy > 0 else 0


        # ----------------------------------------------------
        # SAVE OPTION
        # ----------------------------------------------------

        all_options.append({

            "component":
                name,

            "reduction_percent":
                reduction_percent,

            "new_active":
                new_active,

            "minimum_active":
                minimum_active,

            "component_current_energy":
                current_energy,

            "component_optimized_energy":
                optimized_component_energy,

            "saving":
                saving,

            "system_energy":
                system_energy,

            "system_reduction":
                system_reduction,

            "constraint_status":
                "SATISFIED"
        })


# ============================================================
# SORT OPTIONS
# ============================================================

all_options.sort(
    key=lambda x:
        x["system_energy"]
)


# ============================================================
# DISPLAY TOP OPTIONS
# ============================================================

print("\n" + "=" * 65)

print(
    "TOP FEASIBLE DESIGNS"
)

print("=" * 65)


if len(all_options) == 0:

    print(
        "\nNo feasible optimization "
        "solution found."
    )

else:

    top_options = all_options[:5]


    for number, option in enumerate(
        top_options,
        start=1
    ):

        print(
            "\n" + "-" * 65
        )

        print(
            f"OPTION {number}"
        )

        print(
            f"Component: "
            f"{option['component']}"
        )

        print(
            f"Active-time reduction: "
            f"{option['reduction_percent']:.0f}%"
        )

        print(
            f"New active time: "
            f"{option['new_active']:.2f} min"
        )

        print(
            f"Minimum required: "
            f"{option['minimum_active']:.2f} min"
        )

        print(
            f"System energy: "
            f"{option['system_energy']:.6f} mWh"
        )

        print(
            f"Energy saving: "
            f"{option['saving']:.6f} mWh"
        )

        print(
            f"System reduction: "
            f"{option['system_reduction']:.2f}%"
        )


# ============================================================
# FIND BEST DESIGN
# ============================================================

best = None


if len(all_options) > 0:

    best = all_options[0]


    print("\n" + "=" * 65)

    print(
        "OPTIMAL FEASIBLE DESIGN"
    )

    print("=" * 65)


    print(
        f"\nCurrent system energy: "
        f"{total_current_energy:.6f} mWh"
    )

    print(
        f"Optimized system energy: "
        f"{best['system_energy']:.6f} mWh"
    )

    print(
        f"Energy saving: "
        f"{best['saving']:.6f} mWh"
    )

    print(
        f"System energy reduction: "
        f"{best['system_reduction']:.2f}%"
    )

    print(
        f"\nRecommended component: "
        f"{best['component']}"
    )

    print(
        f"Recommended active-time reduction: "
        f"{best['reduction_percent']:.0f}%"
    )

    print(
        f"New active time: "
        f"{best['new_active']:.2f} min"
    )

    print(
        f"Minimum required active time: "
        f"{best['minimum_active']:.2f} min"
    )

    print(
        "\nConstraint status: SATISFIED"
    )


# ============================================================
# CREATE CSV RESULTS
# ============================================================

csv_rows = []


# ------------------------------------------------------------
# COMPONENT-LEVEL CURRENT DESIGN
# ------------------------------------------------------------

for component in components:

    name = component["name"]

    current_energy = (
        component["current_energy"]
    )

    minimum_active = (
        component["minimum_active"]
    )

    active_duration = (
        component["active_duration"]
    )


    # Check whether this component is
    # the component selected by the best option

    if (
        best is not None
        and best["component"] == name
    ):

        optimized_energy = (
            best["component_optimized_energy"]
        )

        optimized_active = (
            best["new_active"]
        )

        saving = (
            current_energy
            - optimized_energy
        )

        reduction = (

            saving
            / current_energy
            * 100

        ) if current_energy > 0 else 0

        constraint_status = (
            "SATISFIED"
        )

    else:

        optimized_energy = (
            current_energy
        )

        optimized_active = (
            active_duration
        )

        saving = 0.0

        reduction = 0.0

        constraint_status = (
            "NO_CHANGE"
        )


    csv_rows.append({

        "result_type":
            "COMPONENT",

        "component":
            name,

        "current_energy_mwh":
            round(
                current_energy,
                6
            ),

        "optimized_energy_mwh":
            round(
                optimized_energy,
                6
            ),

        "energy_saving_mwh":
            round(
                saving,
                6
            ),

        "reduction_percent":
            round(
                reduction,
                2
            ),

        "current_active_time_min":
            round(
                active_duration,
                4
            ),

        "optimized_active_time_min":
            round(
                optimized_active,
                4
            ),

        "minimum_active_time_min":
            round(
                minimum_active,
                4
            ),

        "constraint_status":
            constraint_status
    })


# ------------------------------------------------------------
# SYSTEM-LEVEL RESULT
# ------------------------------------------------------------

if best is not None:

    csv_rows.append({

        "result_type":
            "SYSTEM",

        "component":
            "TOTAL_SYSTEM",

        "current_energy_mwh":
            round(
                total_current_energy,
                6
            ),

        "optimized_energy_mwh":
            round(
                best["system_energy"],
                6
            ),

        "energy_saving_mwh":
            round(
                best["saving"],
                6
            ),

        "reduction_percent":
            round(
                best["system_reduction"],
                2
            ),

        "current_active_time_min":
            "",

        "optimized_active_time_min":
            "",

        "minimum_active_time_min":
            "",

        "constraint_status":
            "SATISFIED"
    })


# ============================================================
# SAVE TOP FEASIBLE OPTIONS
# ============================================================

if len(all_options) > 0:

    for rank, option in enumerate(
        all_options[:5],
        start=1
    ):

        csv_rows.append({

            "result_type":
                f"TOP_OPTION_{rank}",

            "component":
                option["component"],

            "current_energy_mwh":
                round(
                    total_current_energy,
                    6
                ),

            "optimized_energy_mwh":
                round(
                    option["system_energy"],
                    6
                ),

            "energy_saving_mwh":
                round(
                    option["saving"],
                    6
                ),

            "reduction_percent":
                round(
                    option["system_reduction"],
                    2
                ),

            "current_active_time_min":
                round(
                    option["component_current_energy"],
                    6
                ),

            "optimized_active_time_min":
                round(
                    option["new_active"],
                    4
                ),

            "minimum_active_time_min":
                round(
                    option["minimum_active"],
                    4
                ),

            "constraint_status":
                option["constraint_status"]
        })


# ============================================================
# SAVE CSV
# ============================================================

try:

    results_df = pd.DataFrame(
        csv_rows
    )


    results_df.to_csv(
        OUTPUT_PATH,
        index=False
    )


    print("\n" + "=" * 65)

    print(
        "OPTIMIZATION RESULTS SAVED"
    )

    print("=" * 65)

    print(
        f"\nCSV file:"
    )

    print(
        OUTPUT_PATH
    )

    print(
        f"\nRows saved: "
        f"{len(results_df)}"
    )


except Exception as e:

    print(
        "\nWARNING: Could not save "
        "optimization results."
    )

    print(e)


# ============================================================
# ENGINEERING NOTE
# ============================================================

print("\n" + "=" * 65)

print(
    "ENGINEERING NOTE"
)

print("=" * 65)

print(
    "\nThe optimizer searches multiple "
    "feasible active-time configurations."
)

print(
    "Only configurations satisfying the "
    "minimum active-time constraint "
    "are considered."
)

print(
    "\nResults are calculated estimates "
    "based on the component dataset."
)

print(
    "They do not represent measured "
    "hardware performance."
)

print(
    "Hardware validation using actual "
    "components and INA219 measurements "
    "is required."
)

print(
    "\nCircuitWise AI optimization complete."
)