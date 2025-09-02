#!/usr/bin/env python3
"""
Vérification de la correction du data_processor.py
"""

import duckdb
import pandas as pd

# Charger les nouvelles données
conn = duckdb.connect('data/processed/energy_2h_aggregated.duckdb')
df = conn.execute('SELECT * FROM energy_data').fetchdf()
conn.close()

print("=== VÉRIFICATION DE LA CORRECTION ===")
print(f"Données traitées: {len(df)} lignes")

# Analyser les valeurs
print("\n=== ANALYSE DES VALEURS ===")
print(f"energy_total_kwh: {df['energy_total_kwh'].min():.3f} - {df['energy_total_kwh'].max():.3f} kWh")
print(f"global_active_power_kw: {df['global_active_power_kw'].min():.3f} - {df['global_active_power_kw'].max():.3f} kW")
print(f"sub_metering_1_wh: {df['sub_metering_1_wh'].min():.1f} - {df['sub_metering_1_wh'].max():.1f} Wh")
print(f"sub_metering_2_wh: {df['sub_metering_2_wh'].min():.1f} - {df['sub_metering_2_wh'].max():.1f} Wh")
print(f"sub_metering_3_wh: {df['sub_metering_3_wh'].min():.1f} - {df['sub_metering_3_wh'].max():.1f} Wh")

# Vérifier la cohérence
print("\n=== VÉRIFICATION DE LA COHÉRENCE ===")
total_consumption = df['energy_total_kwh'].sum()
total_sub_meterings = (df['sub_metering_1_wh'].sum() + df['sub_metering_2_wh'].sum() + df['sub_metering_3_wh'].sum()) / 1000

print(f"Consommation totale: {total_consumption:.2f} kWh")
print(f"Somme des sub_meterings: {total_sub_meterings:.2f} kWh")

# Calculer l'énergie non mesurée selon la formule
power_total_wh = df['global_active_power_kw'].sum() * 1000 / 60  # Conversion minute → Wh
unmetered_energy = power_total_wh - (df['sub_metering_1_wh'].sum() + df['sub_metering_2_wh'].sum() + df['sub_metering_3_wh'].sum())
unmetered_kwh = unmetered_energy / 1000

print(f"Énergie non mesurée calculée: {unmetered_kwh:.2f} kWh")
print(f"Énergie totale (non mesurée + sub_meterings): {unmetered_kwh + total_sub_meterings:.2f} kWh")

# Vérifier que c'est cohérent avec energy_total_kwh
difference = abs(total_consumption - (unmetered_kwh + total_sub_meterings))
print(f"Différence: {difference:.2f} kWh")

if difference < 1:
    print("✅ CORRECTION RÉUSSIE - Les données sont maintenant cohérentes !")
else:
    print("❌ Problème persistant")

# Analyser quelques exemples
print("\n=== EXEMPLES DE DONNÉES ===")
sample = df.head(5)
for i, row in sample.iterrows():
    print(f"Ligne {i}: Energy={row['energy_total_kwh']:.3f}kWh, Power={row['global_active_power_kw']:.3f}kW, Sub1={row['sub_metering_1_wh']:.1f}Wh, Sub2={row['sub_metering_2_wh']:.1f}Wh, Sub3={row['sub_metering_3_wh']:.1f}Wh")

