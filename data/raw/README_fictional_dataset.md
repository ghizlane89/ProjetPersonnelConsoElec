# Dataset Énergétique Fictif - Foyer 3 personnes Paris

## 📋 Spécifications

### Période et fréquence
- **Période** : 15/08/2023 → 15/08/2025 (borne de fin exclusive)
- **Fréquence** : Une mesure toutes les 2h (00:00, 02:00, ..., 22:00)
- **Total** : 8,772 lignes

### Profil du foyer
- **Composition** : 3 personnes
- **Localisation** : Paris-like
- **Chauffage** : SANS chauffage électrique
- **ECS** : AVEC ballon électrique
- **Abonnement** : 6 kVA (≈ 30 A)

### Objectifs énergétiques
- **Cible journalière** : 12.0 kWh/jour
- **Cible annuelle** : 4380 kWh/an
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
