
import pandas as pd
import numpy as np
import joblib

from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


print("=" * 70)
print("          CIRCUITWISE AI - V4.4")
print("          ML ENERGY PREDICTION")
print("=" * 70)


# ============================================================
# 1. LOAD DATASET
# ============================================================

dataset_path = Path("D:\pri\ibm\projects\ibm ai project\CircuitWise_AI_ML_Dataset_V4_4.csv")

print("\nLoading ML dataset...")

df = pd.read_csv(dataset_path)

print("Dataset loaded successfully.")
print(f"Number of samples: {len(df)}")


# ============================================================
# 2. DEFINE FEATURES
# ============================================================

features = [
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

target = "target_energy_mwh"


print("\nFeatures used for ML:")

for feature in features:
    print(f"- {feature}")

print(f"\nTarget variable: {target}")


# ============================================================
# 3. CHECK DATA
# ============================================================

print("\n" + "-" * 70)
print("DATASET VALIDATION")
print("-" * 70)

missing_values = df[features + [target]].isnull().sum().sum()

if missing_values > 0:
    print(f"WARNING: {missing_values} missing values found.")
else:
    print("No missing values found in ML features or target.")

print(f"Feature count: {len(features)}")


# ============================================================
# 4. PREPARE X AND Y
# ============================================================

X = df[features]
y = df[target]


# ============================================================
# 5. TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)


print("\n" + "-" * 70)
print("DATASET SPLIT")
print("-" * 70)

print(f"Training samples: {len(X_train)}")
print(f"Testing samples:  {len(X_test)}")


# ============================================================
# 6. CREATE RANDOM FOREST MODEL
# ============================================================

print("\nTraining Random Forest model...")

model = RandomForestRegressor(
    n_estimators=200,
    random_state=42,
    n_jobs=-1
)


# ============================================================
# 7. TRAIN MODEL
# ============================================================

model.fit(X_train, y_train)

print("Model training completed.")


# ============================================================
# 8. SAVE TRAINED MODEL
# ============================================================

model_dir = Path("ml/models")
model_dir.mkdir(parents=True, exist_ok=True)

model_path = model_dir / "power_prediction_model.pkl"

joblib.dump(model, model_path)

print("\nTrained model saved successfully.")
print(f"Model file: {model_path}")


# ============================================================
# 9. PREDICTION
# ============================================================

y_pred = model.predict(X_test)


# ============================================================
# 10. MODEL EVALUATION
# ============================================================

mae = mean_absolute_error(y_test, y_pred)

rmse = np.sqrt(
    mean_squared_error(y_test, y_pred)
)

r2 = r2_score(y_test, y_pred)


print("\n" + "=" * 70)
print("MODEL EVALUATION")
print("=" * 70)

print(f"\nMean Absolute Error (MAE): {mae:.4f} mWh")
print(f"Root Mean Squared Error (RMSE): {rmse:.4f} mWh")
print(f"R² Score: {r2:.4f}")


# ============================================================
# 11. SAMPLE PREDICTIONS
# ============================================================

print("\n" + "=" * 70)
print("SAMPLE PREDICTIONS")
print("=" * 70)

results = pd.DataFrame({
    "Actual Energy (mWh)": y_test.values[:10],
    "Predicted Energy (mWh)": y_pred[:10]
})

results["Error (mWh)"] = (
    results["Actual Energy (mWh)"]
    - results["Predicted Energy (mWh)"]
)

print(results.to_string(index=False))


# ============================================================
# 12. FEATURE IMPORTANCE
# ============================================================

print("\n" + "=" * 70)
print("FEATURE IMPORTANCE")
print("=" * 70)

importance_df = pd.DataFrame({
    "Feature": features,
    "Importance": model.feature_importances_
})

importance_df = importance_df.sort_values(
    by="Importance",
    ascending=False
)

print(
    importance_df.to_string(
        index=False
    )
)


# ============================================================
# 13. FINAL MESSAGE
# ============================================================

print("\n" + "=" * 70)
print("CIRCUITWISE AI V4.4 ML TRAINING COMPLETE")
print("=" * 70)

print("\nSaved model:")
print(model_path)

print("\nThis .pkl file can now be loaded by predict.py")
print("without retraining the Random Forest.")
