import pandas as pd

df = pd.read_csv("railway_safety_dataset.csv")

print("Dataset Shape:")
print(df.shape)

print("\nColumn Names:")
print(df.columns.tolist())

print("\nFirst 5 Records:")
print(df.head())

print("\nRisk Level Counts:")
print(df["risk_level"].value_counts())

print("\nMissing Values:")
print(df.isnull().sum())