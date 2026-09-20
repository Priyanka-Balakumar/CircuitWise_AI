# CircuitWise AI + IBM Bob — Demo Output
## ESP32 + DHT22 Environmental Monitor (60-minute analysis)

> **Status:** Calculated/Simulated — no hardware measurements taken.
> This document captures the demo session results and a representative
> IBM Bob engineering explanation for the project report.

---

## 1. Demo Session Parameters

| Parameter | Value | Source |
|---|---|---|
| System voltage | 3.3 V | —  |
| Analysis period | 60 minutes | — |
| ESP32 active current | 23.88 mA | Espressif official datasheet |
| ESP32 sleep current | 0.00814 mA | Espressif official datasheet |
| ESP32 peak current | 240.0 mA | Espressif official datasheet |
| DHT22 active current | 2.5 mA | Adafruit / AM2302 product documentation |
| DHT22 sleep current | *no datasheet value* | Null — not zero |

| Component | Active (min) | Sleep (min) | Peak (min) | Min. active constraint |
|---|---|---|---|---|
| ESP32 | 10 | 48 | 2 | 5 min |
| DHT22 / AM2302 | 60 | 0 | 0 | 60 min |

---

## 2. Engineering Calculation Results (Calculated)

Formula: `P (mW) = V (V) × I (mA)` ; `E (mWh) = P × (duration_min / 60)`

| Component | Mode | Current (mA) | Duration (min) | Energy (mWh) |
|---|---|---|---|---|
| ESP32 | Active | 23.88 | 10 | 13.134 |
| ESP32 | Sleep | 0.00814 | 48 | 0.021 |
| ESP32 | Peak | 240.0 | 2 | 26.400 |
| ESP32 | **Total** | — | — | **39.555** |
| DHT22 | Active | 2.5 | 60 | 8.250 |
| DHT22 | **Total** | — | — | **8.250** |
| **SYSTEM TOTAL** | — | — | — | **47.805 mWh** |

> These are **calculated** values from datasheet current specifications.
> They are NOT hardware measurements.

---

## 3. ML Prediction Results (Predicted)

| Field | Value |
|---|---|
| ML predicted energy | **22.417 mWh** |
| Calculated energy | 47.805 mWh |
| Difference | −25.388 mWh |
| Absolute difference | **53.11%** |
| Interpretation band | `significant_deviation` |
| Model | RandomForestRegressor(n_estimators=200, random_state=42) |
| Training data | Synthetic/calculated (V4.4 dataset) |

> The 53.11% deviation is **model behaviour on synthetic data**, not a physical discrepancy.
> The training dataset was generated from the same formulas; the model learned patterns in
> that data which do not necessarily generalise to configurations with very high peak currents
> (240 mA peak is at the upper extreme of the training distribution, explaining the larger error).
> Hardware validation is required to determine real-world accuracy.

---

## 4. Anomaly Detection Results (Statistical)

### Dataset Summary
| Metric | Value |
|---|---|
| Total configurations analysed | 1,500 |
| Normal configurations | 1,425 (95.0%) |
| Anomalous configurations | 75 (5.0%) |
| Model contamination parameter | 5% (expected) |

### Closest Demo Config Match
| Field | Value |
|---|---|
| Configuration ID | 1471 |
| Components in matched config | ESP32-S3 + BMP280 |
| Component count | 2 |
| Voltage | 3.3 V |
| Period | 60 min |
| Calculated energy | 134.107 mWh |
| Anomaly score | +0.177 |
| Anomaly status | **NORMAL** |

> **Interpretation:** The closest matching configuration (2 components, 3.3 V, 60 min) was
> classified as NORMAL with a score of +0.177. Scores above 0 are typical.
>
> **Important:** "ANOMALY" means statistically unusual relative to the synthetic training dataset.
> It does NOT mean a hardware fault, an unsafe design, or an incorrect calculation.

---

## 5. Optimization Results (Simulated)

### System-Level Summary
| Metric | Value |
|---|---|
| Current system energy | 21.406 mWh |
| Best optimized energy | 14.842 mWh |
| Best energy saving | **6.565 mWh** |
| Best reduction | **30.67%** |

> Note: The optimization was run with a different ESP32 profile (10 min active, 50 min sleep, 0 min peak).
> The `session_input.json` demo uses 2 min peak, which increases calculated energy above the optimizer run.

### Per-Component
| Component | Current energy | Optimized energy | Saving | Status |
|---|---|---|---|---|
| ESP32 | 13.156 mWh | 6.592 mWh | 6.565 mWh (49.9%) | SATISFIED |
| DHT22 / AM2302 | 8.250 mWh | 8.250 mWh | 0.0 mWh (0.0%) | NO_CHANGE |

> **DHT22 cannot be optimized** — its minimum active time constraint is 60 min (same as the period).
> The optimizer correctly identifies no reduction is possible without breaking functionality.

### Top Optimization Options
| Rank | ESP32 active time | System energy | System saving | Reduction |
|---|---|---|---|---|
| TOP_OPTION_1 | 5.0 min | 14.842 mWh | **6.565 mWh** | **30.67%** |
| TOP_OPTION_2 | 5.5 min | 15.498 mWh | 5.908 mWh | 27.60% |
| TOP_OPTION_3 | 6.0 min | 16.155 mWh | 5.252 mWh | 24.53% |
| TOP_OPTION_4 | 6.5 min | 16.811 mWh | 4.595 mWh | 21.47% |
| TOP_OPTION_5 | 7.0 min | 17.468 mWh | 3.939 mWh | 18.40% |

> All options satisfy the ESP32 minimum active time constraint of 5 min.
> These are **calculated/simulated** estimates. No experimental energy savings have been measured.

---

## 6. Engine-Generated Recommendations

The CircuitWise AI Python engine generated the following recommendations for this session:

1. **ESP32 peak current is 240.00 mA.** Review peak-load events and power supply capacity.
   *(The ESP32's Wi-Fi TX peak is the dominant energy cost in this session — 26.4 mWh of 47.8 mWh total.)*

2. **DHT22 / AM2302: no defensible sleep current in the dataset.** Consider reducing active duty cycle
   if the application allows it.
   *(The DHT22 has no documented sleep mode. It must remain active for the full analysis period.)*

3. **DHT22 / AM2302: active for 60.00 minutes.** Reducing active duty cycle may reduce energy.
   *(The DHT22 max sampling rate is 0.5 Hz — measurement every 2 seconds. If the application
   can tolerate less frequent readings, a microcontroller-controlled power gate could reduce effective
   active time. This is a future design consideration.)*

---

## 7. Representative IBM Bob Engineering Explanation

*The following is a representative Bob response based on the verified results in `circuitwise_results.json`,
produced using the `bob_prompt.md` constraint file. This documents the expected Bob workflow for the
project report.*

---

> **Bob's Engineering Explanation — ESP32 + DHT22, 60-minute analysis**
>
> ### Energy Summary
>
> The CircuitWise AI Python engine calculated a total system energy consumption of **47.81 mWh**
> for the ESP32 + DHT22 configuration over 60 minutes at 3.3 V supply.
>
> Breaking this down:
> - The **ESP32** accounts for **39.56 mWh** (82.7% of total). The dominant energy cost is the
>   Wi-Fi/RF peak burst: 240 mA for 2 minutes = 26.4 mWh. This single event consumes more energy
>   than the entire DHT22 sensor over the full hour.
> - The **DHT22** accounts for **8.25 mWh** (17.3%). It draws a steady 2.5 mA with no sleep capability
>   in the current dataset.
> - The ESP32 **deep sleep** at 0.00814 mA for 48 minutes contributes only 0.02 mWh — demonstrating
>   how effective deep sleep can be.
>
> The **ML model predicted 22.42 mWh** — a 53.11% deviation from the calculated value.
>
> This large deviation falls into the `significant_deviation` band. It indicates that the RandomForest
> model, trained on synthetic configurations, encounters difficulty with this particular combination
> of a very low sleep current (0.00814 mA) and a very high peak current (240 mA) in the same
> configuration. This is not a hardware discrepancy — it reflects the boundary conditions of the
> training distribution. Hardware validation with an INA219 would reveal the true measured energy
> and allow this model to be improved.
>
> ### Anomaly Detection Summary
>
> Across the 1,500 synthetic configurations in the dataset, the IsolationForest model classified
> 75 (5.0%) as anomalous and 1,425 (95.0%) as normal. This matches the contamination parameter
> set at training time.
>
> The closest matching configuration to the demo session (2 components, 3.3 V, 60 min) was
> configuration #1471 (ESP32-S3 + BMP280), classified as **NORMAL** with a score of +0.177.
>
> An anomaly score above zero means the configuration is well within the typical range of the
> training data. A classification of NORMAL does **not** mean the design is guaranteed safe —
> it means it is statistically similar to configurations the model saw during training.
> Conversely, an ANOMALY classification would mean the configuration is statistically unusual,
> **not** that there is a confirmed hardware fault.
>
> ### Optimization Recommendations
>
> The constraint-aware optimizer found that the ESP32 active time can be reduced from 10 min
> to as low as 5 min (the minimum active time constraint) while maintaining full system functionality.
>
> The top optimization option (TOP_OPTION_1) reduces system energy by **6.565 mWh (30.67%)**
> — from 21.41 mWh to 14.84 mWh. This is achieved by reducing ESP32 active time by 5 minutes
> and reallocating that time to deep sleep.
>
> The DHT22 cannot be optimized — its minimum active time equals the full analysis period.
>
> These are **calculated/simulated estimates**. The actual energy saving achievable on real hardware
> may differ and should be verified with an INA219 measurement.
>
> ### Engine Recommendations
>
> The CircuitWise AI engine identified three design considerations:
> 1. The 240 mA peak current is the primary energy cost and power supply concern.
> 2. The DHT22 has no documented sleep mode — consider a power gate if less frequent sampling is acceptable.
> 3. The DHT22 is active 100% of the analysis period — sampling rate reduction could reduce energy.
>
> ### Assumptions and Limitations
>
> - All current values are from datasheets under specific measurement conditions.
>   Real hardware current draws vary with temperature, supply voltage, software state, and RF environment.
> - The ML model was trained on synthetic data generated from the same formulas.
>   Its accuracy on real hardware is unknown until validated.
> - Optimization savings are from discrete 5%-step scenarios. The true optimum may lie between steps.
> - No uncertainty quantification (confidence intervals) is provided.
>
> ### Next Steps
>
> To validate these results, connect an INA219 current sensor in series with the ESP32 power supply,
> run the same 60-minute operating profile on physical hardware, and compare the measured energy
> against the calculated 47.81 mWh. This will establish whether the engineering calculation,
> the ML model, or both need refinement.
>
> ---
>
> **Data Limitations Notice:**
> All values in this analysis are calculated or simulated using synthetic training data derived
> from component datasheets. No experimental hardware measurements have been taken.
> Hardware validation using ESP32 + INA219 is planned as a future project phase.
> These results are suitable for learning, estimation, and academic demonstration purposes.
> They must not be used as the sole basis for real system design without hardware validation.

---

## 8. Responsible AI Summary

| Concern | Status |
|---|---|
| All values labelled by source | ✅ Calculated / Predicted / Simulated |
| Synthetic data explicitly disclosed | ✅ In JSON, in Bob prompt, in every Bob response |
| ML prediction ≠ hardware measurement | ✅ Enforced by bob_prompt.md |
| Anomaly ≠ hardware fault | ✅ Enforced by bob_prompt.md and field glossary |
| Optimization savings labelled simulated | ✅ In JSON constraint_note and Bob prompt |
| Minimum active time constraints enforced | ✅ By optimizer.py |
| Hardware validation disclaimer | ✅ Required in every Bob response |
| Privacy: no personal data | ✅ Only electrical parameters |
| Measured values | ❌ None yet — ESP32 + INA219 planned |

---

## 9. Files Created by This Integration

| File | Purpose |
|---|---|
| `bob_context/export_results.py` | Reads CSVs, populates JSON anomaly + optimization sections |
| `bob_context/export_prediction.py` | Runs engineering calc + ML inference, populates JSON prediction section |
| `bob_context/session_input.json` | Demo session parameters (ESP32 + DHT22 defaults) |
| `bob_context/circuitwise_results.json` | Generated: all verified outputs in one place |
| `bob_context/bob_prompt.md` | Bob's role definition, constraints, prohibitions, disclaimer |
| `bob_context/run_bob_session.py` | Single-command pipeline orchestrator |
| `bob_context/bob_session_context.txt` | Generated: paste into Bob VS Code chat |
| `bob_context/demo_output.md` | This file — captured demo results for project report |
| `RESPONSIBLE_AI.md` | Full responsible AI documentation |

**No existing files were modified.**

---

*Generated by CircuitWise AI + IBM Bob integration pipeline.*
*All numerical values sourced from `bob_context/circuitwise_results.json` — no values invented.*
