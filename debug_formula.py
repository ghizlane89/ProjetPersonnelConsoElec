#!/usr/bin/env python3
"""
Debug de la formule d'énergie totale
"""

import duckdb
import pandas as pd

# Charger les données
conn = duckdb.connect('data/processed/energy_2h_aggregated.duckdb')
df = conn.execute('SELECT * FROM energy_data').fetchdf()
conn.close()

print("=== DEBUG DE LA FORMULE ===")

# Analyser une ligne spécifique
row = df.iloc[0]
print(f"Exemple ligne 0:")
print(f"  global_active_power_kw: {row['global_active_power_kw']}")
print(f"  sub_metering_1_wh: {row['sub_metering_1_wh']}")
print(f"  sub_metering_2_wh: {row['sub_metering_2_wh']}")
print(f"  sub_metering_3_wh: {row['sub_metering_3_wh']}")
print(f"  energy_total_kwh: {row['energy_total_kwh']}")

# Calculer manuellement
power_wh = row['global_active_power_kw'] * 1000 / 60  # Conversion minute → Wh
sub_total = row['sub_metering_1_wh'] + row['sub_metering_2_wh'] + row['sub_metering_3_wh']
unmetered = power_wh - sub_total
unmetered_kwh = unmetered / 1000

print(f"\nCalcul manuel:")
print(f"  power_wh = {row['global_active_power_kw']} * 1000 / 60 = {power_wh:.2f} Wh")
print(f"  sub_total = {sub_total:.2f} Wh")
print(f"  unmetered = {power_wh:.2f} - {sub_total:.2f} = {unmetered:.2f} Wh")
print(f"  unmetered_kwh = {unmetered_kwh:.3f} kWh")

# Vérifier si c'est négatif
if unmetered < 0:
    print(f"⚠️ Énergie non mesurée négative ! Cela signifie que les sub_meterings dépassent la puissance totale.")
    print(f"   Cela peut arriver si les données sont incorrectes ou si la formule ne s'applique pas.")

# Analyser plusieurs lignes
print(f"\n=== ANALYSE DE PLUSIEURS LIGNES ===")
for i in range(5):
    row = df.iloc[i]
    power_wh = row['global_active_power_kw'] * 1000 / 60
    sub_total = row['sub_metering_1_wh'] + row['sub_metering_2_wh'] + row['sub_metering_3_wh']
    unmetered = power_wh - sub_total
    
    print(f"Ligne {i}: Power={row['global_active_power_kw']:.1f}kW → {power_wh:.1f}Wh, Sub={sub_total:.1f}Wh, Unmetered={unmetered:.1f}Wh")

