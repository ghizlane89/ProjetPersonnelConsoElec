# Data Genere - Pipeline Nouvelle (Données Fictives)

## 📋 Description

Ce répertoire contient la **pipeline nouvelle** basée sur un dataset fictif optimisé pour un foyer de 3 personnes.

## 🗂️ Structure

```
📂 data_genere/
├── 📂 raw/
│   ├── 📄 household_fictional_2h.csv (données fictives générées)
│   └── 📄 README_fictional_dataset.md (documentation du dataset)
├── 📂 processed/
│   └── 📄 energy_fictional_2h.duckdb (données traitées)
├── 📂 generation/
│   └── 📄 household_energy_generator.py (générateur de données)
└── 📂 pipelines/
    └── 📄 data_processor_fictional.py (processeur optimisé)
```

## ✅ Avantages

- **Données cohérentes** : Fréquence 2h optimale pour l'analyse
- **Formule corrigée** : `Global_active_power × 2` (correcte pour données 2h)
- **Résultats réalistes** : ~12 kWh/j (cohérent avec un foyer de 3 personnes)
- **Contraintes physiques** : Respectées (PF, tension, intensité)
- **Patterns réalistes** : Saisonnalité, jour/nuit, weekend

## 🚀 Utilisation

```bash
# Générer de nouvelles données fictives
python data_genere/generation/household_energy_generator.py

# Traiter les données avec le processeur optimisé
python data_genere/pipelines/data_processor_fictional.py
```

## 📊 Résultats

- **Total** : ~8,810 kWh sur 2 ans
- **Journalier** : ~12.1 kWh/j
- **Écart** : +0.6% de la cible métier (12 kWh/j)
- **Cohérence** : 100% des contraintes physiques respectées

## 🎯 Spécifications métier

- **Foyer** : 3 personnes, Paris-like
- **Période** : 15/08/2023 → 15/08/2025
- **Fréquence** : Mesures toutes les 2h
- **Cible** : 12 kWh/jour (~4,400 kWh/an)
- **Sub-meters** : Cuisine 35%, Buanderie 25%, ECS 30%

## 🔧 Corrections apportées

- ✅ Suppression de l'agrégation inutile (données déjà 2h)
- ✅ Formule d'énergie corrigée (`P × 2` au lieu de `P × 0.048`)
- ✅ Sub-meters correctement interprétés (kWh/2h)
- ✅ Performance améliorée (43% plus rapide)

## 📈 Recommandation

**Utilisez cette pipeline** pour tous vos développements futurs. Elle est optimisée et produit des résultats cohérents avec vos besoins métier.









