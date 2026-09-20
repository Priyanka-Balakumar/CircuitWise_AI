import pandas as pd

DATASET_PATH = "D:\pri\ibm\projects\ibm ai project\CircuitWise_AI_ML_Dataset.csv"

df = pd.read_csv(DATASET_PATH)

print("=" * 60)
print("CIRCUITWISE AI - ML DATASET CHECK")
print("=" * 60)

print("\nDataset loaded successfully!")

print("\nShape:")
print(df.shape)

print("\nColumns:")
for column in df.columns:
    print("-", column)

print("\nFirst 5 rows:")
print(df.head())

print("\nMissing values:")
print(df.isnull().sum())

print("\nDataset information:")
print(df.info())