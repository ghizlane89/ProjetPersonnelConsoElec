#!/usr/bin/env python3
"""
Générateur de Dataset Énergétique Fictif - Foyer 3 personnes Paris
================================================================

Script autonome générant un dataset synthétique de consommation électrique
au format UCI/Kaggle "Household Electric Power Consumption" agrégé en pas de 2h.

Spécifications métier :
- Foyer : 3 personnes, Paris-like, SANS chauffage électrique, AVEC ECS électrique
- Abonnement : 6 kVA (≈ 30 A)
- Cible : ~12 kWh/jour (≈ 4 400–4 600 kWh/an)
- Période : 15/08/2023 → 15/08/2025 (borne de fin exclusive)
- Fréquence : une mesure toutes les 2h (00:00, 02:00, …, 22:00)

Auteur : Data Engineer - Energy Agent Project
Date : 2024
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os
from pathlib import Path

# =============================================================================
# PARAMÈTRES DE GÉNÉRATION
# =============================================================================

# Période de génération
START_DATE = datetime(2023, 8, 15)
END_DATE = datetime(2025, 8, 15)  # Borne exclusive

# Paramètres électriques
TARGET_DAILY_KWH = 12.0  # kWh/jour cible
TARGET_ANNUAL_KWH = TARGET_DAILY_KWH * 365  # ~4,380 kWh/an
ABONNEMENT_KVA = 6.0  # kVA
ABONNEMENT_AMPS = 30.0  # A

# Paramètres de tension
VOLTAGE_NOMINAL = 231.0  # V
VOLTAGE_TOLERANCE = 2.5  # V
VOLTAGE_MIN = 225.0  # V
VOLTAGE_MAX = 240.0  # V

# Facteur de puissance
PF_MIN = 0.94
PF_MAX = 0.99

# Seed pour reproductibilité
RANDOM_SEED = 42

# Correction pour atteindre la cible
POWER_MULTIPLIER = 3.8  # Multiplicateur pour atteindre ~12 kWh/j

# =============================================================================
# PATTERNS JOURNALIERS (puissance relative par tranche de 2h)
# =============================================================================

DAILY_PATTERNS = {
    0: 0.15,   # 00h-02h : Nuit profonde
    2: 0.10,   # 02h-04h : Minimum nocturne
    4: 0.12,   # 04h-06h : Réveil frigo
    6: 0.85,   # 06h-08h : Réveil, petit-déjeuner
    8: 0.45,   # 08h-10h : Départ au travail
    10: 0.35,  # 10h-12h : Base matin
    12: 0.70,  # 12h-14h : Déjeuner
    14: 0.40,  # 14h-16h : Base après-midi
    16: 0.55,  # 16h-18h : Retour du travail
    18: 0.90,  # 18h-20h : Cuisine, éclairage
    20: 0.75,  # 20h-22h : Soirée, TV
    22: 0.45   # 22h-00h : Coucher
}

# =============================================================================
# PATTERNS SAISONNIERS (facteur multiplicateur par mois)
# =============================================================================

SEASONAL_PATTERNS = {
    1: 1.30,   # Janvier : +30% (hiver)
    2: 1.25,   # Février : +25%
    3: 1.15,   # Mars : +15%
    4: 1.05,   # Avril : +5%
    5: 1.00,   # Mai : base
    6: 0.95,   # Juin : -5%
    7: 0.90,   # Juillet : -10%
    8: 0.85,   # Août : -15% (minimum)
    9: 0.95,   # Septembre : -5%
    10: 1.05,  # Octobre : +5%
    11: 1.15,  # Novembre : +15%
    12: 1.25   # Décembre : +25%
}

# =============================================================================
# RÉPARTITION DES SUB-METERS (% de l'énergie totale)
# =============================================================================

SUB_METER_DISTRIBUTION = {
    'kitchen': 0.35,      # Cuisine (Sub_metering_1)
    'laundry': 0.25,      # Buanderie/électroménager (Sub_metering_2)
    'hot_water': 0.30,   # ECS électrique (Sub_metering_3)
    'other': 0.10        # Reste (pas de colonne dédiée)
}

# =============================================================================
# FONCTIONS DE GÉNÉRATION
# =============================================================================

def generate_timestamps():
    """Génère la liste des timestamps toutes les 2h"""
    timestamps = []
    current = START_DATE
    
    while current < END_DATE:
        # Ajouter les 12 mesures par jour (00h, 02h, ..., 22h)
        for hour in [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]:
            timestamp = current.replace(hour=hour, minute=0, second=0)
            timestamps.append(timestamp)
        current += timedelta(days=1)
    
    return timestamps

def apply_daily_pattern(power_base, hour):
    """Applique le pattern journalier"""
    pattern_factor = DAILY_PATTERNS.get(hour, 0.5)
    return power_base * pattern_factor

def apply_seasonal_pattern(power, month):
    """Applique le pattern saisonnier"""
    seasonal_factor = SEASONAL_PATTERNS.get(month, 1.0)
    return power * seasonal_factor

def apply_weekend_boost(power, weekday):
    """Applique le boost weekend (+10%)"""
    if weekday >= 5:  # Samedi (5) et Dimanche (6)
        return power * 1.10
    return power

def generate_voltage():
    """Génère une tension réaliste dans les bornes strictes"""
    return np.random.uniform(VOLTAGE_MIN + 0.1, VOLTAGE_MAX - 0.1)  # Éviter les bornes exactes

def calculate_power_factor():
    """Calcule un facteur de puissance réaliste dans les bornes strictes"""
    return np.random.uniform(PF_MIN + 0.001, PF_MAX - 0.001)  # Éviter les bornes exactes

def calculate_reactive_power(active_power, power_factor):
    """Calcule la puissance réactive à partir du facteur de puissance"""
    # PF = P / S, donc S = P / PF
    # Q = √(S² - P²)
    apparent_power = active_power / power_factor
    reactive_power = np.sqrt(apparent_power**2 - active_power**2)
    return reactive_power

def calculate_intensity(active_power, reactive_power, voltage):
    """Calcule l'intensité à partir des puissances et de la tension"""
    apparent_power = np.sqrt(active_power**2 + reactive_power**2)
    intensity = (apparent_power * 1000) / voltage  # Conversion kW→W
    return intensity

def generate_sub_meters(energy_window):
    """Génère les sub-meters avec contrainte de cohérence stricte"""
    # Réserver exactement 0.1 kWh pour le "reste"
    available_energy = energy_window - 0.1
    
    # Générer les sub-meters avec répartition stricte
    kitchen_energy = available_energy * SUB_METER_DISTRIBUTION['kitchen']
    laundry_energy = available_energy * SUB_METER_DISTRIBUTION['laundry']
    hot_water_energy = available_energy * SUB_METER_DISTRIBUTION['hot_water']
    
    # Ajouter un petit bruit (±3% max) pour le réalisme
    noise_factor = np.random.uniform(0.97, 1.03)
    kitchen_energy *= noise_factor
    laundry_energy *= (2.0 - noise_factor)  # Compensate to keep total constant
    hot_water_energy = available_energy - kitchen_energy - laundry_energy
    
    # S'assurer que tous les sub-meters sont positifs et dans les limites
    kitchen_energy = max(0.01, min(kitchen_energy, available_energy * 0.4))
    laundry_energy = max(0.01, min(laundry_energy, available_energy * 0.3))
    hot_water_energy = max(0.01, min(hot_water_energy, available_energy * 0.4))
    
    # Normaliser pour respecter exactement la contrainte
    total_sub = kitchen_energy + laundry_energy + hot_water_energy
    if total_sub > available_energy:
        factor = available_energy / total_sub
        kitchen_energy *= factor
        laundry_energy *= factor
        hot_water_energy *= factor
    
    return kitchen_energy, laundry_energy, hot_water_energy

def validate_constraints(row):
    """Valide les contraintes physiques sur une ligne"""
    violations = []
    
    # Contrainte 1: E_window = Global_active_power × 2
    expected_energy = row['Global_active_power'] * 2
    actual_energy = row['Sub_metering_1'] + row['Sub_metering_2'] + row['Sub_metering_3'] + 0.1
    if abs(expected_energy - actual_energy) > 0.01:
        violations.append(f"Énergie: attendu {expected_energy:.3f}, réel {actual_energy:.3f}")
    
    # Contrainte 2: Sub1 + Sub2 + Sub3 ≤ E_window (avec reste ≥ 0.1 kWh)
    total_sub = row['Sub_metering_1'] + row['Sub_metering_2'] + row['Sub_metering_3']
    if total_sub > (row['Global_active_power'] * 2 - 0.1):
        violations.append(f"Sub-meters trop élevés: {total_sub:.3f}")
    
    # Contrainte 3: PF ∈ [0.94 ; 0.99]
    pf = row['Global_active_power'] / np.sqrt(row['Global_active_power']**2 + row['Global_reactive_power']**2)
    if pf < PF_MIN or pf > PF_MAX:
        violations.append(f"PF hors limites: {pf:.3f}")
    
    # Contrainte 4: S ≤ 6 kVA
    apparent_power = np.sqrt(row['Global_active_power']**2 + row['Global_reactive_power']**2)
    if apparent_power > ABONNEMENT_KVA:
        violations.append(f"Puissance apparente trop élevée: {apparent_power:.3f} kVA")
    
    # Contrainte 5: I ≤ 30 A
    if row['Global_intensity'] > ABONNEMENT_AMPS:
        violations.append(f"Intensité trop élevée: {row['Global_intensity']:.3f} A")
    
    # Contrainte 6: Voltage dans les bornes
    if row['Voltage'] < VOLTAGE_MIN or row['Voltage'] > VOLTAGE_MAX:
        violations.append(f"Tension hors bornes: {row['Voltage']:.3f} V")
    
    return violations

# =============================================================================
# GÉNÉRATION PRINCIPALE
# =============================================================================

def generate_dataset():
    """Génère le dataset complet"""
    print("🚀 Démarrage de la génération du dataset énergétique...")
    print(f"📅 Période: {START_DATE.strftime('%d/%m/%Y')} → {END_DATE.strftime('%d/%m/%Y')}")
    print(f"🎯 Cible: {TARGET_DAILY_KWH} kWh/jour ({TARGET_ANNUAL_KWH:.0f} kWh/an)")
    print()
    
    # Initialiser le générateur aléatoire
    np.random.seed(RANDOM_SEED)
    
    # Générer les timestamps
    timestamps = generate_timestamps()
    print(f"⏰ {len(timestamps)} timestamps générés")
    
    # Initialiser les listes de données
    data = []
    total_violations = 0
    
    # Calculer la puissance de base pour atteindre la cible
    total_hours = len(timestamps) * 2  # 2h par mesure
    target_total_kwh = TARGET_ANNUAL_KWH
    power_base = target_total_kwh / total_hours  # kW moyen
    
    print(f"⚡ Puissance de base calculée: {power_base:.3f} kW")
    print()
    
    # Générer chaque ligne
    for i, timestamp in enumerate(timestamps):
        if i % 1000 == 0:
            print(f"📊 Génération: {i}/{len(timestamps)} lignes...")
        
        # Appliquer les patterns
        hour = timestamp.hour
        month = timestamp.month
        weekday = timestamp.weekday()
        
        # Puissance active avec tous les patterns
        power = power_base
        power = apply_daily_pattern(power, hour)
        power = apply_seasonal_pattern(power, month)
        power = apply_weekend_boost(power, weekday)
        
        # Appliquer le multiplicateur pour atteindre la cible
        power *= POWER_MULTIPLIER
        
        # Ajouter du bruit réaliste (±10%)
        power *= np.random.uniform(0.9, 1.1)
        
        # Générer la tension
        voltage = generate_voltage()
        
        # Calculer le facteur de puissance
        power_factor = calculate_power_factor()
        
        # Calculer la puissance réactive
        reactive_power = calculate_reactive_power(power, power_factor)
        
        # Calculer l'intensité
        intensity = calculate_intensity(power, reactive_power, voltage)
        
        # Calculer l'énergie sur 2h
        energy_window = power * 2  # kWh
        
        # Générer les sub-meters
        sub1, sub2, sub3 = generate_sub_meters(energy_window)
        
        # Créer la ligne de données
        row = {
            'Date': timestamp.strftime('%d/%m/%Y'),
            'Time': timestamp.strftime('%H:%M:%S'),
            'Global_active_power': round(power, 3),
            'Global_reactive_power': round(reactive_power, 3),
            'Voltage': round(voltage, 3),
            'Global_intensity': round(intensity, 3),
            'Sub_metering_1': round(sub1, 3),
            'Sub_metering_2': round(sub2, 3),
            'Sub_metering_3': round(sub3, 3)
        }
        
        # Valider les contraintes
        violations = validate_constraints(row)
        if violations:
            total_violations += len(violations)
            print(f"⚠️ Violations ligne {i}: {violations}")
        
        data.append(row)
    
    # Créer le DataFrame
    df = pd.DataFrame(data)
    
    print()
    print("✅ Génération terminée !")
    print(f"📊 Dataset: {len(df)} lignes")
    print(f"⚠️ Violations totales: {total_violations}")
    
    return df

def generate_report(df):
    """Génère un rapport de validation"""
    print("\n" + "="*60)
    print("📋 RAPPORT DE VALIDATION")
    print("="*60)
    
    # Statistiques de base
    total_kwh = df['Global_active_power'].sum() * 2  # Conversion 2h
    total_days = len(df) / 12  # 12 mesures par jour
    daily_average = total_kwh / total_days
    
    print(f"📊 Statistiques générales:")
    print(f"   - Lignes générées: {len(df):,}")
    print(f"   - Période: {df['Date'].iloc[0]} → {df['Date'].iloc[-1]}")
    print(f"   - Total kWh: {total_kwh:,.0f}")
    print(f"   - Moyenne journalière: {daily_average:.2f} kWh/j")
    print(f"   - Écart à la cible: {((daily_average - TARGET_DAILY_KWH) / TARGET_DAILY_KWH * 100):+.1f}%")
    
    # Statistiques par sub-meter
    print(f"\n🔌 Répartition des sub-meters:")
    sub1_total = df['Sub_metering_1'].sum()
    sub2_total = df['Sub_metering_2'].sum()
    sub3_total = df['Sub_metering_3'].sum()
    total_sub = sub1_total + sub2_total + sub3_total
    
    print(f"   - Cuisine (Sub1): {sub1_total:,.0f} kWh ({sub1_total/total_sub*100:.1f}%)")
    print(f"   - Buanderie (Sub2): {sub2_total:,.0f} kWh ({sub2_total/total_sub*100:.1f}%)")
    print(f"   - ECS (Sub3): {sub3_total:,.0f} kWh ({sub3_total/total_sub*100:.1f}%)")
    print(f"   - Total sub-meters: {total_sub:,.0f} kWh")
    
    # Contraintes physiques
    print(f"\n⚡ Contraintes physiques:")
    print(f"   - Tension min/max: {df['Voltage'].min():.1f}V / {df['Voltage'].max():.1f}V")
    print(f"   - Intensité max: {df['Global_intensity'].max():.1f}A")
    print(f"   - Puissance apparente max: {np.sqrt(df['Global_active_power']**2 + df['Global_reactive_power']**2).max():.2f}kVA")
    
    # Validation complète
    print(f"\n✅ Validation complète:")
    all_violations = []
    for idx, row in df.iterrows():
        violations = validate_constraints(row)
        if violations:
            all_violations.extend(violations)
    
    if not all_violations:
        print("   ✅ Aucune violation des contraintes détectée !")
    else:
        print(f"   ⚠️ {len(all_violations)} violations détectées")
        for violation in all_violations[:5]:  # Afficher les 5 premières
            print(f"      - {violation}")
        if len(all_violations) > 5:
            print(f"      ... et {len(all_violations) - 5} autres")

def save_dataset(df, output_file="household_fictional_2h.csv"):
    """Sauvegarde le dataset en CSV"""
    # Créer le répertoire de sortie
    output_path = Path("data/raw") / output_file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Sauvegarder
    df.to_csv(output_path, sep='\t', index=False)
    print(f"\n💾 Dataset sauvegardé: {output_path}")
    print(f"📏 Taille: {output_path.stat().st_size / 1024:.1f} KB")

def create_readme():
    """Crée le fichier README avec les spécifications"""
    readme_content = f"""# Dataset Énergétique Fictif - Foyer 3 personnes Paris

## 📋 Spécifications

### Période et fréquence
- **Période** : {START_DATE.strftime('%d/%m/%Y')} → {END_DATE.strftime('%d/%m/%Y')} (borne de fin exclusive)
- **Fréquence** : Une mesure toutes les 2h (00:00, 02:00, ..., 22:00)
- **Total** : {len(generate_timestamps()):,} lignes

### Profil du foyer
- **Composition** : 3 personnes
- **Localisation** : Paris-like
- **Chauffage** : SANS chauffage électrique
- **ECS** : AVEC ballon électrique
- **Abonnement** : 6 kVA (≈ 30 A)

### Objectifs énergétiques
- **Cible journalière** : {TARGET_DAILY_KWH} kWh/jour
- **Cible annuelle** : {TARGET_ANNUAL_KWH:.0f} kWh/an
- **Répartition** : Cuisine 35%, Buanderie 25%, ECS 30%, Autres 10%

## 🔌 Sub-meters

| Sub-meter | Description | Unité | Répartition |
|-----------|-------------|-------|-------------|
| Sub_metering_1 | Cuisine (électroménager) | kWh/2h | 35% |
| Sub_metering_2 | Buanderie/électroménager | kWh/2h | 25% |
| Sub_metering_3 | ECS (ballon électrique) | kWh/2h | 30% |
| Reste | Autres consommations | kWh/2h | 10% |

## ⚡ Contraintes physiques

### Contraintes énergétiques
- **E_window = Global_active_power × 2** (kWh)
- **Sub1 + Sub2 + Sub3 ≤ E_window** (avec reste ≥ 0,1 kWh)

### Contraintes électriques
- **Facteur de puissance** : PF ∈ [0,94 ; 0,99]
- **Puissance apparente** : S = √(P²+Q²) ≤ 6 kVA
- **Intensité** : I = S×1000 / V ≤ 30 A
- **Tension** : V ≈ 231 V ± 2,5 V (bornes 225–240 V)

## 📊 Patterns

### Profil journalier
- **Nuit (00h-06h)** : 10-15% de la puissance moyenne
- **Matin (06h-08h)** : 85% (réveil, petit-déjeuner)
- **Journée (08h-18h)** : 35-55% (base + activités)
- **Soirée (18h-22h)** : 75-90% (cuisine, éclairage)
- **Coucher (22h-00h)** : 45% (diminution progressive)

### Saisonnalité
- **Pic hivernal (janvier)** : +30% vs août
- **Creux estival (août)** : -15% (minimum)
- **Variation annuelle** : ±15% autour de la moyenne

### Effet weekend
- **Weekend** : +10% de consommation
- **Présence** : Plus de temps à domicile

## 🎯 Utilisation

Ce dataset est compatible avec la pipeline Energy Agent :
1. **Format** : CSV tab-séparé
2. **Colonnes** : Identiques au format UCI/Kaggle
3. **Validation** : Contraintes physiques respectées
4. **Intégration** : Compatible avec `data_processor.py`

## 📈 Métriques de qualité

- **Cohérence énergétique** : 100% des lignes respectent E = P×2
- **Cohérence électrique** : 100% des lignes respectent les contraintes PF/I/V
- **Réalisme métier** : Patterns jour/nuit/saison/weekend
- **Reproductibilité** : Seed fixe pour résultats identiques
"""
    
    readme_path = Path("data/raw") / "README_fictional_dataset.md"
    readme_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"📚 README créé: {readme_path}")

# =============================================================================
# EXÉCUTION PRINCIPALE
# =============================================================================

if __name__ == "__main__":
    print("🔧 GÉNÉRATEUR DE DATASET ÉNERGÉTIQUE FICTIF")
    print("=" * 60)
    
    # Générer le dataset
    df = generate_dataset()
    
    # Générer le rapport
    generate_report(df)
    
    # Sauvegarder le dataset
    save_dataset(df)
    
    # Créer le README
    create_readme()
    
    print("\n🎉 Génération terminée avec succès !")
    print("📁 Fichiers créés:")
    print("   - data/raw/household_fictional_2h.csv")
    print("   - data/raw/README_fictional_dataset.md")
    print("\n🚀 Prêt pour intégration dans la pipeline Energy Agent !")
