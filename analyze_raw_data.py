#!/usr/bin/env python3
"""
Vérification des données brutes
"""

import pandas as pd

# Charger les données brutes
df_raw = pd.read_csv('data/raw/household.csv', sep='\t')

print("=== ANALYSE DES DONNÉES BRUTES ===")
print(f"Dimensions: {df_raw.shape[0]} lignes x {df_raw.shape[1]} colonnes")

# Analyser les colonnes
print("\n=== COLONNES ===")
for col in df_raw.columns:
    print(f"  {col}")

# Analyser quelques lignes
print("\n=== EXEMPLES DE DONNÉES BRUTES ===")
sample = df_raw.head(10)
for i, row in sample.iterrows():
    print(f"Ligne {i}: Date={row['Date']}, Time={row['Time']}, Power={row['Global_active_power']}, Sub1={row['Sub_metering_1']}, Sub2={row['Sub_metering_2']}, Sub3={row['Sub_metering_3']}")

# Statistiques
print("\n=== STATISTIQUES ===")
print(f"Global_active_power: {df_raw['Global_active_power'].min():.3f} - {df_raw['Global_active_power'].max():.3f}")
print(f"Sub_metering_1: {df_raw['Sub_metering_1'].min():.1f} - {df_raw['Sub_metering_1'].max():.1f}")
print(f"Sub_metering_2: {df_raw['Sub_metering_2'].min():.1f} - {df_raw['Sub_metering_2'].max():.1f}")
print(f"Sub_metering_3: {df_raw['Sub_metering_3'].min():.1f} - {df_raw['Sub_metering_3'].max():.1f}")

# Vérifier la cohérence sur quelques lignes
print("\n=== VÉRIFICATION COHÉRENCE ===")
for i in range(5):
    row = df_raw.iloc[i]
    power = row['Global_active_power']
    sub1 = row['Sub_metering_1']
    sub2 = row['Sub_metering_2']
    sub3 = row['Sub_metering_3']
    sub_total = sub1 + sub2 + sub3
    
    print(f"Ligne {i}: Power={power:.3f}, Sub1={sub1:.1f}, Sub2={sub2:.1f}, Sub3={sub3:.1f}, Sub_total={sub_total:.1f}")
    if power > 0:
        ratio = sub_total / (power * 1000) if power * 1000 > 0 else 0
        print(f"  Ratio sub_total/power: {ratio:.3f}")

