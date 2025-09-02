#!/usr/bin/env python3
"""
Analyse détaillée des données brutes pour comprendre les unités
"""

import pandas as pd

# Charger les données brutes
df_raw = pd.read_csv('data/raw/household.csv', sep='\t')

print("=== ANALYSE DÉTAILLÉE DES UNITÉS ===")

# Analyser la cohérence physique
print("\n=== VÉRIFICATION PHYSIQUE ===")
for i in range(10):
    row = df_raw.iloc[i]
    power = row['Global_active_power']  # kW
    voltage = row['Voltage']  # V
    intensity = row['Global_intensity']  # A
    
    # Vérifier P = U * I
    calculated_power = voltage * intensity / 1000  # W → kW
    difference = abs(power - calculated_power)
    
    print(f"Ligne {i}: P={power:.3f}kW, U={voltage:.1f}V, I={intensity:.1f}A")
    print(f"  P calculé = {voltage:.1f} * {intensity:.1f} / 1000 = {calculated_power:.3f} kW")
    print(f"  Différence = {difference:.3f} kW")
    
    if difference < 0.1:
        print(f"  ✅ Cohérent")
    else:
        print(f"  ⚠️ Incohérent")

# Analyser la cohérence avec les sub_meterings
print("\n=== VÉRIFICATION AVEC SUB_METERINGS ===")
for i in range(5):
    row = df_raw.iloc[i]
    power = row['Global_active_power']  # kW
    sub1 = row['Sub_metering_1']  # Wh
    sub2 = row['Sub_metering_2']  # Wh
    sub3 = row['Sub_metering_3']  # Wh
    
    # Si power est en kW par minute, alors l'énergie en Wh = power * 60
    energy_from_power = power * 60  # kWh → Wh
    sub_total = sub1 + sub2 + sub3
    
    print(f"Ligne {i}: Power={power:.3f}kW → {energy_from_power:.1f}Wh")
    print(f"  Sub_total = {sub1:.1f} + {sub2:.1f} + {sub3:.1f} = {sub_total:.1f} Wh")
    print(f"  Ratio = {sub_total/energy_from_power:.3f}")

print("\n=== CONCLUSION ===")
print("Si Global_active_power est en kW par minute:")
print("- L'énergie par minute = power * 60 Wh")
print("- Les sub_meterings sont en Wh")
print("- Le ratio devrait être < 1 (car sub_meterings < énergie totale)")
print("- Si le ratio > 1, alors power n'est pas en kW par minute")

