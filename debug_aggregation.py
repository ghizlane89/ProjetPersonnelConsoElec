#!/usr/bin/env python3
"""
Debug de l'agrégation
"""

import duckdb
import pandas as pd

# Charger les données
conn = duckdb.connect('data/processed/energy_2h_aggregated.duckdb')
df = conn.execute('SELECT * FROM energy_data').fetchdf()
conn.close()

print("=== DEBUG DE L'AGRÉGATION ===")

# Analyser les valeurs aberrantes
print("Valeurs global_active_power_kw > 10 kW:")
high_power = df[df['global_active_power_kw'] > 10]
print(f"Nombre de lignes: {len(high_power)}")

if len(high_power) > 0:
    print("Exemples:")
    for i, row in high_power.head(5).iterrows():
        print(f"  Ligne {i}: {row['global_active_power_kw']:.1f} kW, {row['measurement_count']} mesures")

# Vérifier le nombre de mesures
print(f"\nNombre de mesures par agrégation:")
print(f"Min: {df['measurement_count'].min()}")
print(f"Max: {df['measurement_count'].max()}")
print(f"Moyenne: {df['measurement_count'].mean():.1f}")

# Analyser une ligne avec beaucoup de mesures
high_count = df[df['measurement_count'] > 100].iloc[0]
print(f"\nExemple ligne avec beaucoup de mesures:")
print(f"  measurement_count: {high_count['measurement_count']}")
print(f"  global_active_power_kw: {high_count['global_active_power_kw']:.1f}")
print(f"  sub_metering_1_wh: {high_count['sub_metering_1_wh']:.1f}")
print(f"  sub_metering_2_wh: {high_count['sub_metering_2_wh']:.1f}")
print(f"  sub_metering_3_wh: {high_count['sub_metering_3_wh']:.1f}")

# Le problème : on fait une moyenne de puissances, mais on devrait faire une somme
# car Global_active_power est déjà une énergie par minute
print(f"\nPROBLÈME IDENTIFIÉ:")
print(f"  On fait une moyenne de Global_active_power, mais c'est déjà une énergie par minute")
print(f"  Il faut faire une somme, pas une moyenne !")

