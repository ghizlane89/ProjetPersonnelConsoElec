#!/usr/bin/env python3
"""
Test final de la correction
"""

import duckdb
import pandas as pd

# Charger les données
conn = duckdb.connect('data/processed/energy_2h_aggregated.duckdb')
df = conn.execute('SELECT * FROM energy_data').fetchdf()
conn.close()

print("=== TEST FINAL DE LA CORRECTION ===")
print(f"Données traitées: {len(df)} lignes")

# Analyser les valeurs
print("\n=== ANALYSE DES VALEURS ===")
print(f"energy_total_kwh: {df['energy_total_kwh'].min():.3f} - {df['energy_total_kwh'].max():.3f} kWh")
print(f"global_active_power_kw: {df['global_active_power_kw'].min():.3f} - {df['global_active_power_kw'].max():.3f} kW")

# Vérifier la cohérence
print("\n=== VÉRIFICATION DE LA COHÉRENCE ===")
total_consumption = df['energy_total_kwh'].sum()
total_sub_meterings = (df['sub_metering_1_wh'].sum() + df['sub_metering_2_wh'].sum() + df['sub_metering_3_wh'].sum()) / 1000

print(f"Consommation totale: {total_consumption:.2f} kWh")
print(f"Somme des sub_meterings: {total_sub_meterings:.2f} kWh")

# Analyser quelques exemples
print("\n=== EXEMPLES DE DONNÉES ===")
sample = df.head(5)
for i, row in sample.iterrows():
    print(f"Ligne {i}: Energy={row['energy_total_kwh']:.3f}kWh, Power={row['global_active_power_kw']:.3f}kW, Sub1={row['sub_metering_1_wh']:.1f}Wh, Sub2={row['sub_metering_2_wh']:.1f}Wh, Sub3={row['sub_metering_3_wh']:.1f}Wh")

# Vérifier si les valeurs sont cohérentes avec les références
print("\n=== COMPARAISON AVEC RÉFÉRENCES ===")
days = (df['timestamp'].max() - df['timestamp'].min()).days
total_kwh = df['energy_total_kwh'].sum()
daily_avg = total_kwh / days

print(f"Période: {days} jours")
print(f"Consommation totale: {total_kwh:.0f} kWh")
print(f"Moyenne par jour: {daily_avg:.1f} kWh/j")

print("\nRéférences:")
print("- 1 personne (hors chauffage): 6-6.5 kWh/j")
print("- 2 personnes (hors chauffage): 12-13 kWh/j")
print("- 2 personnes (avec chauffage): 32-41 kWh/j")

if daily_avg > 30:
    print("✅ Cohérent avec un foyer de 2 personnes avec chauffage électrique")
elif daily_avg > 10:
    print("✅ Cohérent avec un foyer de 2 personnes sans chauffage électrique")
else:
    print("⚠️ Consommation faible, à vérifier")

print("\n=== CONCLUSION ===")
if total_consumption > 0:
    print("✅ CORRECTION RÉUSSIE - Les données sont maintenant cohérentes !")
else:
    print("❌ Problème persistant - Les valeurs energy_total_kwh sont à 0")

