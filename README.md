# ⚡ CircuitWise AI

## AI-Assisted Energy-Efficient Design for IoT Devices

> **Calculate. Predict. Detect. Optimize. Explain.**

CircuitWise AI is an AI-assisted engineering system designed to help engineers and IoT developers analyze, predict, and optimize the energy consumption of electronic and IoT device configurations.

The system combines **deterministic electrical calculations, machine learning, anomaly detection, constraint-aware optimization, and IBM BOB-assisted explanation** to support more energy-conscious IoT design decisions.

The project is developed as part of the **1M1B × IBM SkillsBuild × AICTE AI for Sustainability Virtual Internship**.

---

## 📌 Project Overview

IoT devices frequently operate under power constraints because they may depend on batteries, energy-limited embedded systems, or low-power operating environments.

During the design process, engineers may need to:

* Check component datasheets
* Compare operating currents
* Calculate power consumption
* Estimate energy requirements
* Analyze active, idle, sleep, and peak modes
* Identify energy-intensive components
* Estimate battery requirements
* Explore lower-energy configurations

These tasks can become repetitive when several components and operating scenarios are involved.

**CircuitWise AI** aims to provide a structured software workflow for this analysis.

The system accepts an IoT configuration and processes it through:

```text
Component Selection
        ↓
Power Calculation
        ↓
Energy Prediction
        ↓
Anomaly Detection
        ↓
Optimization
        ↓
IBM BOB Explanation
        ↓
Engineering Insights
```

---

# 🎯 Problem Statement

Designing energy-efficient IoT systems often requires repeated manual analysis of component specifications and operating conditions.

For a configuration such as:

```text
ESP32
+
DHT22
+
Display
+
Wireless Communication
+
Battery
```

an engineer may need to determine:

* How much power each component consumes
* How operating modes affect total energy
* Which component contributes most to energy consumption
* How long a battery may operate the system
* Whether a configuration is unusual compared with other designs
* Whether operating schedules can be optimized

### Problem

> **How can AI assist engineers in analyzing and optimizing the energy consumption of IoT systems before physical hardware testing?**

---

# 💡 Proposed Solution

CircuitWise AI provides an integrated software workflow consisting of five major stages:

### 1. Calculate

Determine power and energy consumption using engineering equations and component specifications.

### 2. Predict

Use a machine-learning model to estimate expected energy consumption for a configuration.

### 3. Detect

Identify statistically unusual configurations using anomaly detection.

### 4. Optimize

Search for lower-energy operating scenarios while respecting user-defined constraints.

### 5. Explain

Use IBM BOB as an AI-assisted development and explanation layer to interpret results and generate engineering-oriented recommendations.

---

# 🌱 Sustainability Goal

## Primary UN Sustainable Development Goal

### **SDG 12 — Responsible Consumption and Production**

CircuitWise AI supports SDG 12 by encouraging responsible and energy-conscious design of electronic and IoT systems.

The project focuses on:

* Reducing unnecessary energy consumption
* Identifying energy-intensive operating conditions
* Encouraging efficient component utilization
* Supporting energy-aware design decisions
* Moving energy analysis earlier in the product-design process

### Supporting SDGs

The project can also contribute to:

* **SDG 7 — Affordable and Clean Energy**
* **SDG 9 — Industry, Innovation and Infrastructure**
* **SDG 13 — Climate Action**

SDG 12 remains the **primary alignment** of the project.

---

# 🧠 AI Components

CircuitWise AI combines multiple AI/ML techniques.

## 1. Machine Learning Energy Prediction

A **Random Forest regression model** is used to predict energy consumption.

### Input features

The model uses configuration-level features such as:

* Component count
* System voltage
* Analysis period
* Active duration
* Sleep duration
* Peak duration
* Average active current
* Average sleep current
* Average peak current

### Model evaluation

The current model was evaluated using generated/component-derived test data.

Results:

| Metric |      Result |
| ------ | ----------: |
| MAE    |  ~93.17 mWh |
| RMSE   | ~293.01 mWh |
| R²     |      ~0.948 |

### Important limitation

These results are **not hardware-validation results**.

The current ML dataset is synthetic/component-derived and was created for software prototyping and model development.

Therefore, the project does **not** claim that the model currently predicts real hardware energy consumption with 94.8% accuracy.

The value **R² = 0.948** represents the model's coefficient of determination on the generated test dataset.

---

# 🔎 2. Anomaly Detection

CircuitWise AI uses **Isolation Forest** to identify statistically unusual configurations.

Current configuration dataset:

```text
Total configurations: 1,500

Normal:                1,425
Flagged as anomalies:     75
```

The configured contamination value is:

```text
0.05
```

Therefore, approximately 5% of the generated dataset is expected to be flagged.

### Important interpretation

The **5% figure is not a real-world IoT failure rate or fault probability**.

It represents the configured anomaly-detection contamination level used in the software experiment.

An anomaly means that a configuration is statistically unusual relative to the dataset; it does not automatically mean that the hardware is defective.

---

# ⚙️ 3. Constraint-Aware Optimization

The optimization module searches for lower-energy operating scenarios while respecting constraints.

For example:

```text
ESP32 active time:
10 minutes → 5 minutes
```

with a user-defined minimum active time of:

```text
5 minutes
```

For the tested optimization scenario, the optimizer calculated a potential:

### **30.67% reduction in system energy**

This result is a **calculated/simulated optimization scenario**.

It is not a measured hardware reduction.

The optimization engine is designed to prevent unrealistic recommendations by respecting minimum operating requirements.

---

# 💬 4. IBM BOB Integration

IBM BOB is integrated into CircuitWise AI as an **AI-assisted software development, analysis, explanation, and documentation layer**.

IBM describes Bob as an AI SDLC partner capable of working with real codebases, generating and modifying code, explaining code, creating documentation, running commands, and supporting specialized workflows through modes such as Agent, Plan, and Ask.

In CircuitWise AI, BOB is used to:

* Understand the project context
* Assist with development workflows
* Analyze project outputs
* Explain calculated and ML results
* Interpret anomaly-detection results
* Explain optimization scenarios
* Generate structured demonstration output
* Support responsible-AI documentation

### BOB workflow

```text
CircuitWise Results
        ↓
BOB Project Context
        ↓
AI-Assisted Analysis
        ↓
Explanation
        ↓
Engineering Recommendations
```

### Important architectural decision

IBM BOB does **not** replace the deterministic electrical calculations.

The engineering baseline remains:

```text
Power:
P = V × I

Energy:
E = P × t
```

The ML model provides an estimate.

BOB explains and contextualizes the results.

---

# 🏗️ System Architecture

```text
                         USER / ENGINEER
                                │
                                ▼
                    ┌────────────────────┐
                    │ Configuration Input│
                    │                    │
                    │ Components         │
                    │ Voltage            │
                    │ Operating Modes    │
                    │ Time               │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │ Component Database │
                    │                    │
                    │ Datasheet-derived  │
                    │ specifications     │
                    └─────────┬──────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
           ┌────────────────┐   ┌────────────────┐
           │ Power & Energy │   │ ML Prediction  │
           │ Calculation    │   │ Random Forest  │
           └───────┬────────┘   └───────┬────────┘
                   │                    │
                   └─────────┬──────────┘
                             ▼
                   ┌──────────────────┐
                   │ Anomaly Detection│
                   │  IsolationForest │
                   └────────┬─────────┘
                            │
                            ▼
                   ┌──────────────────┐
                   │   Optimization   │
                   │ Constraint-aware │
                   └────────┬─────────┘
                            │
                            ▼
                   ┌──────────────────┐
                   │    IBM BOB       │
                   │ Explanation &    │
                   │ AI Assistance    │
                   └────────┬─────────┘
                            │
                            ▼
                   Engineering Insights
```

---

# 🔬 Engineering Calculation Layer

CircuitWise AI uses deterministic calculations as the engineering baseline.

## Power

For electrical power:

```text
P = V × I
```

where:

* `P` = power
* `V` = voltage
* `I` = current

When voltage is in volts and current is in milliamps:

```text
P(mW) = V(V) × I(mA)
```

## Energy

For a time period:

```text
E = P × t
```

When power is expressed in mW and time in hours:

```text
E(mWh) = P(mW) × t(hours)
```

For minute-based calculations:

```text
E(mWh) = P(mW) × t(minutes) / 60
```

These deterministic calculations provide the baseline against which the ML prediction can be compared.

---

# 📊 Component Dataset

The current component dataset contains **15 electronic/IoT components**.

| Component                | Category             |
| ------------------------ | -------------------- |
| ESP32                    | MCU                  |
| ESP32-S3                 | MCU                  |
| Raspberry Pi Pico        | MCU Board            |
| Arduino Uno / ATmega328P | MCU Board            |
| DHT22 / AM2302           | Sensor               |
| MPU6050                  | IMU Sensor           |
| BMP280                   | Pressure Sensor      |
| HC-SR04                  | Ultrasonic Sensor    |
| HC-SR501                 | PIR Sensor           |
| DS18B20                  | Temperature Sensor   |
| HC-05                    | Bluetooth Module     |
| nRF24L01+                | RF Transceiver       |
| SSD1306                  | Display Controller   |
| INA219                   | Power Monitor        |
| BME280                   | Environmental Sensor |

The dataset includes information such as:

* Supply voltage
* Typical voltage
* Active current
* Idle current
* Sleep current
* Peak current
* Typical power
* Communication type
* Measurement conditions
* Source information
* Data-quality classification

---

# 📚 Data Quality Approach

The project follows several principles when handling component specifications.

### Manufacturer information is preferred

Component specifications are based on manufacturer datasheets or product information wherever possible.

### Missing values are not automatically zero

If a source does not provide a defensible value, the field may remain blank.

A blank value does **not** mean zero power consumption.

### Operating conditions matter

Current consumption depends on:

* Operating mode
* Voltage
* Communication activity
* Measurement conditions
* Hardware implementation

Therefore, component values should not be interpreted as universal measurements for every possible implementation.

---

# 🧪 Current Demonstration

The current demonstration uses:

```text
Component 1: ESP32
Component 2: DHT22

Voltage: 3.3 V
Analysis period: 60 minutes
```

The prototype processes this configuration through the CircuitWise workflow.

---

# 📈 Example Demo Results

For the current demonstration profile:

### Deterministic calculation

```text
Calculated energy ≈ 47.81 mWh
```

### ML prediction

```text
Predicted energy ≈ 22.42 mWh
```

### Difference

```text
Difference ≈ 25.39 mWh
Relative deviation ≈ 53.1%
```

### Interpretation

The difference demonstrates that the current ML model does not perfectly reproduce the deterministic calculation for every configuration.

Possible reasons include:

* Synthetic training data
* Limited component dataset
* Distribution differences
* Feature representation
* Limited hardware validation
* Model behavior at unusual configurations

The difference is **not treated as a physical measurement discrepancy**.

The deterministic calculation remains the engineering baseline until hardware measurements are available.

---

# 🚨 Example Anomaly Analysis

The current anomaly dataset contains:

```text
1,500 total configurations
1,425 normal
75 flagged
```

The anomaly module uses Isolation Forest.

The output can be used to identify configurations that are statistically unusual within the generated dataset.

### Interpretation rule

```text
Anomaly ≠ Hardware Fault
```

An anomaly indicates unusual statistical characteristics in the model's feature space.

It should not automatically be interpreted as:

* Component failure
* Hardware damage
* Safety issue
* Incorrect circuit design

Real-world fault detection would require measured hardware data and appropriate validation.

---

# ⚙️ Example Optimization

The optimizer can search operating-time reductions while respecting constraints.

Example:

```text
ESP32 active time:
Current:     10 min
Optimized:    5 min

Minimum allowed:
              5 min
```

For the tested scenario:

```text
Current scenario energy:     21.406 mWh
Optimized scenario energy:  14.842 mWh

Calculated saving:            6.565 mWh
Potential reduction:         30.67%
```

### Important

This optimization scenario is separate from the 47.81 mWh demonstration profile containing a peak-current period.

Therefore:

> **30.67% should not be interpreted as a measured 30.67% reduction of the 47.81 mWh demonstration.**

It is a calculated result for a specific optimization scenario.

---

# 🛡️ Responsible AI

Responsible AI is an important part of CircuitWise AI.

## Transparency

The system distinguishes between:

```text
Calculated
Predicted
Simulated
Measured
```

These categories are not intentionally mixed.

## Data Transparency

The current ML dataset is synthetic/component-derived.

This is explicitly documented.

## Human Oversight

CircuitWise AI provides decision support.

The system does not autonomously approve or certify an engineering design.

## No Fabricated Measurements

The system does not claim to have measured hardware power when hardware measurements have not been performed.

## Limitations

Current limitations include:

* No physical hardware validation
* Synthetic/component-derived ML dataset
* Limited number of components
* Limited operating profiles
* Model performance may vary outside the training distribution
* Optimization depends on user-defined constraints

---

# 🔌 Future Hardware Validation

The next major development stage is hardware validation.

### Planned setup

```text
ESP32
  │
  ▼
INA219 Power Monitor
  │
  ▼
Load / Sensors
```

The INA219 will provide actual electrical measurements that can be compared with:

```text
1. Deterministic calculation
2. ML prediction
3. Optimization scenario
4. Actual measured energy
```

---

# 🔄 Future ML Pipeline

Once real hardware measurements become available:

```text
Hardware Testing
       ↓
Power Measurements
       ↓
Measured Dataset
       ↓
Data Cleaning
       ↓
Feature Engineering
       ↓
Model Retraining
       ↓
Model Evaluation
       ↓
Real-World Validation
```

This can gradually replace or supplement the current synthetic training data.

---

# 🚀 Future Scope

Potential future improvements include:

### Larger Component Database

Expand from the current 15 components to a much larger set of:

* MCUs
* Sensors
* Displays
* Communication modules
* Power-management ICs
* Actuators

### Real-Time Monitoring

Integrate ESP32 and INA219 for live current/power measurements.

### Battery-Life Prediction

Estimate battery operating time under realistic duty cycles.

### Alternative Component Recommendation

Suggest lower-energy alternatives while considering:

* Voltage
* Functionality
* Communication requirements
* Current consumption
* Cost

### Hardware-in-the-Loop Validation

Connect the software optimization workflow to physical devices.

### Dashboard

Develop a visual interface for:

* Component selection
* Energy analysis
* ML prediction
* Anomaly detection
* Optimization
* Historical measurements

---

# 📁 Project Structure

```text
CircuitWise-AI/
│
├── README.md
├── RESPONSIBLE_AI.md
│
├── CircuitWise_AI_Component_Power_Dataset.xlsx
├── CircuitWise_AI_ML_Dataset.csv
├── CircuitWise_AI_ML_Dataset_V4_4.csv
│
├── data/
│   ├── CircuitWise_AI_Anomaly_Results.csv
│   └── CircuitWise_AI_Optimization_Results.csv
│
├── power_model/
│   └── power_calculator.py
│
├── ml/
│   ├── check_dataset.py
│   ├── train.py
│   ├── predict.py
│   ├── anomaly_detection.py
│   ├── optimizer.py
│   └── models/
│       └── power_prediction_model.pkl
│
├── bob_context/
│   ├── bob_prompt.md
│   ├── bob_session_context.txt
│   ├── circuitwise_results.json
│   ├── demo_output.md
│   ├── export_prediction.py
│   ├── export_results.py
│   ├── run_bob_session.py
│   └── session_input.json
│
└── docs/
    ├── architecture.md
    ├── methodology.md
    └── responsible_ai.md
```

> The exact repository structure may evolve as the project develops.

---

# 💻 Technology Stack

## Programming

* Python 3.10

## Data Processing

* Pandas
* NumPy
* OpenPyXL

## Machine Learning

* Scikit-learn
* Random Forest
* Isolation Forest

## Model Persistence

* Joblib

## Visualization / Analysis

* Matplotlib

## AI Development Assistance

* IBM BOB

## Planned Hardware

* ESP32
* INA219

---

# ⚙️ Installation

## 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd CircuitWise-AI
```

Replace `<YOUR_GITHUB_REPOSITORY_URL>` with the actual GitHub repository URL.

---

## 2. Create a virtual environment

Python 3.10 is recommended for the current project.

### Windows

```powershell
python -m venv .venv
```

Activate it in PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Or use Command Prompt:

```cmd
.venv\Scripts\activate
```

---

## 3. Install dependencies

```bash
pip install pandas numpy openpyxl matplotlib scikit-learn joblib
```

If a `requirements.txt` file is included:

```bash
pip install -r requirements.txt
```

---

# ▶️ Running the Project

## Power Calculation

Run:

```bash
python power_model/power_calculator.py
```

The calculator allows component and operating-mode selection and calculates power/energy values.

---

## Dataset Check

Run:

```bash
python ml/check_dataset.py
```

This can be used to verify the ML dataset structure before training.

---

## Train the ML Model

Run:

```bash
python ml/train.py
```

The training script:

1. Loads the ML dataset
2. Selects prediction features
3. Splits the dataset
4. Trains the Random Forest model
5. Evaluates the model
6. Saves the trained model

The model is saved under:

```text
ml/models/power_prediction_model.pkl
```

---

## Generate Predictions

Run:

```bash
python ml/predict.py
```

The prediction module loads the trained model and produces energy predictions for supported configurations.

---

## Anomaly Detection

Run:

```bash
python ml/anomaly_detection.py
```

The anomaly results are saved to:

```text
data/CircuitWise_AI_Anomaly_Results.csv
```

---

## Optimization

Run:

```bash
python ml/optimizer.py
```

Optimization results are saved to:

```text
data/CircuitWise_AI_Optimization_Results.csv
```

---

# 🤖 IBM BOB Workflow

IBM BOB was used during the project development process to support planning, implementation, analysis, explanation, and documentation.

IBM's documentation describes a workflow where Bob can plan before implementation, implement through Agent mode, explain code through Ask mode, and use tools for reading files, editing code, and running commands.

CircuitWise AI uses a controlled workflow in which the existing engineering logic remains the foundation.

### Project workflow

```text
Requirements
     ↓
Planning
     ↓
Implementation
     ↓
Validation
     ↓
BOB Analysis
     ↓
Explanation
     ↓
Documentation
```

### Bob-specific project files

```text
bob_context/
```

contains supporting files such as:

* Project prompt
* Session context
* Session input
* Result exports
* Demo output
* Bob session runner

---

# 📊 Evaluation Philosophy

CircuitWise AI separates different types of evidence.

## Level 1 — Engineering Calculation

Based on equations and component specifications.

Example:

```text
P = V × I
E = P × t
```

## Level 2 — ML Prediction

Based on a trained machine-learning model.

## Level 3 — Simulation / Optimization

Based on software-generated scenarios and constraints.

## Level 4 — Hardware Measurement

Future stage using physical hardware and an INA219 power monitor.

### Evidence hierarchy

```text
Calculated
    ↓
ML Prediction
    ↓
Simulation
    ↓
Hardware Measurement
```

Hardware measurement will provide the strongest validation for real-world energy consumption.

---

# ⚠️ Limitations

CircuitWise AI is currently a **software prototype**.

The following limitations apply:

### 1. No hardware measurements yet

The current results have not been validated against physical ESP32/DHT22 hardware.

### 2. Synthetic/component-derived ML data

The current ML model is trained on generated/component-derived configurations.

### 3. Limited component database

The prototype currently contains 15 components.

### 4. Model generalization

Predictions may be less reliable for configurations outside the training distribution.

### 5. Optimization assumptions

Optimization results depend on user-defined operating constraints.

### 6. No universal component behavior

Actual power consumption depends on implementation, operating conditions, firmware, communication activity, and hardware configuration.

---

# 🔐 Responsible Use

CircuitWise AI should be treated as an **engineering decision-support tool**.

It should not be used as the sole basis for:

* Safety-critical design decisions
* Production certification
* Electrical compliance claims
* Battery safety decisions
* Guaranteed lifetime predictions

Physical measurements and appropriate engineering validation are required before production deployment.

---

# 📈 Expected Impact

If developed further and validated with hardware, CircuitWise AI could help:

### Engineers

* Reduce repetitive power calculations
* Identify energy-intensive operating conditions
* Explore optimization scenarios earlier

### IoT Developers

* Estimate energy requirements
* Plan battery-powered designs
* Compare operating strategies

### MSMEs

* Perform early-stage energy analysis
* Reduce dependence on repeated manual experimentation
* Explore energy-efficient product concepts

### Students

* Learn the integration of:

  * Electronics
  * Machine Learning
  * Data Analysis
  * AI-assisted development
  * Sustainable engineering

### Sustainability

The project promotes energy-aware design decisions and supports the broader goal of responsible resource consumption.

---

# 🧩 Example Use Case

Consider an environmental monitoring IoT device:

```text
ESP32
+
DHT22
+
OLED
+
Wi-Fi
+
Battery
```

An engineer can use CircuitWise AI to:

```text
1. Select components
       ↓
2. Enter voltage
       ↓
3. Define operating durations
       ↓
4. Calculate baseline energy
       ↓
5. Generate ML prediction
       ↓
6. Check for unusual configuration
       ↓
7. Explore optimization options
       ↓
8. Ask IBM BOB to explain the results
```

The engineer can then validate the final design using physical measurements.

---

# 🧪 Validation Roadmap

| Stage                         | Method                      | Status     |
| ----------------------------- | --------------------------- | ---------- |
| Component data collection     | Datasheet/component sources | ✅          |
| Deterministic calculator      | Python                      | ✅          |
| ML dataset generation         | Synthetic/component-derived | ✅          |
| ML model                      | Random Forest               | ✅          |
| Anomaly detection             | Isolation Forest            | ✅          |
| Optimization                  | Constraint-aware software   | ✅          |
| IBM BOB integration           | AI-assisted workflow        | ✅          |
| Hardware measurement          | ESP32 + INA219              | 🔄 Planned |
| Real measurement dataset      | Hardware-generated          | 🔄 Planned |
| Model retraining              | Real data                   | 🔄 Planned |
| Hardware-in-loop optimization | Future                      | 🔄 Planned |

---

# 📌 Key Project Results

### Current software prototype

```text
15
Components
```

```text
1,500
Generated ML Configurations
```

```text
R² ≈ 0.948
ML Model Test Result
```

```text
1,425
Normal Configurations
```

```text
75
Configured Anomalies
```

```text
30.67%
Calculated Optimization Scenario
```

> These figures represent the current software prototype and should not be interpreted as physical hardware performance measurements.

---

# 🌍 Sustainability Impact Statement

CircuitWise AI aims to shift energy analysis from a late-stage testing activity toward an **early-stage design consideration**.

### Conventional workflow

```text
Design
  ↓
Build
  ↓
Test
  ↓
Discover High Power
  ↓
Redesign
```

### CircuitWise AI workflow

```text
Design
  ↓
Analyze
  ↓
Predict
  ↓
Detect
  ↓
Optimize
  ↓
Build
  ↓
Validate
```

The intended impact is to help engineers consider energy consumption earlier in the design process.

---

# 🔮 Future Vision

The long-term goal is to evolve CircuitWise AI from a software analysis prototype into a **hardware-validated intelligent energy optimization platform**.

Future architecture:

```text
              USER
                │
                ▼
        CircuitWise AI
                │
      ┌─────────┼─────────┐
      ▼         ▼         ▼
   Calculate  Predict  Optimize
      │         │         │
      └─────────┼─────────┘
                ▼
          IBM BOB
        Explanation
                │
                ▼
             ESP32
                │
                ▼
             INA219
                │
                ▼
       Real Power Data
                │
                ▼
        Continuous ML
          Improvement
```

---

# 👨‍💻 Author

**[Your Name]**

Electronics & Communication Engineering
**[Your College Name]**

5th Semester

Project developed for:

**1M1B × IBM SkillsBuild × AICTE AI for Sustainability Virtual Internship**

---

# 📜 Project Status

### Current Status: **Working Software Prototype**

Implemented:

* ✅ Component power database
* ✅ Deterministic power calculation
* ✅ Energy calculation
* ✅ Multi-component analysis
* ✅ Energy-profile analysis
* ✅ Machine-learning prediction
* ✅ Random Forest model
* ✅ Isolation Forest anomaly detection
* ✅ Constraint-aware optimization
* ✅ IBM BOB integration
* ✅ Responsible AI documentation
* ✅ Demo result generation

Planned:

* 🔄 ESP32 hardware validation
* 🔄 INA219 measurement integration
* 🔄 Real-world measurement dataset
* 🔄 ML retraining using measured data
* 🔄 Real-time monitoring
* 🔄 Interactive dashboard

---

# ⭐ Key Takeaway

CircuitWise AI combines **electronics engineering, machine learning, optimization, AI-assisted development, and sustainability** into a single workflow.

> **The objective is not to replace engineers with AI.**

> **The objective is to give engineers better information earlier in the design process.**

### **Calculate. Predict. Detect. Optimize. Explain.**

---

# 📄 License

This project is developed as an academic/prototype project.

A formal open-source license can be added before public distribution.

---

# 🙏 Acknowledgements

* **1M1B**
* **IBM SkillsBuild**
* **IBM BOB**
* **AICTE**
* **UN Sustainable Development Goals**
* Component manufacturers and publicly available technical documentation used for component specifications

---

# 🔗 References

* IBM BOB Documentation: [IBM BOB Documentation](https://bob.ibm.com/docs/ide?utm_source=chatgpt.com)
* IBM BOB AI Coding Agent: [IBM AI Coding Agent](https://www.ibm.com/products/ai-coding-agent?utm_source=chatgpt.com)
* UN Sustainable Development Goals: [United Nations Sustainable Development Goals](https://sdgs.un.org/goals?utm_source=chatgpt.com)

---

## ⭐ CircuitWise AI

**AI-assisted energy optimization for sustainable IoT design.**

**Design Smarter. Predict Earlier. Optimize Energy. Build Sustainably.**
