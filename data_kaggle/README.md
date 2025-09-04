# Data Kaggle - Pipeline Ancienne (Données UCI)

## 📋 Description

Ce répertoire contient la **pipeline ancienne** basée sur le dataset UCI "Household Electric Power Consumption".

## 🗂️ Structure

```
📂 data_kaggle/
├── 📂 raw/
│   └── 📄 household.csv (données originales UCI)
├── 📂 processed/
│   └── 📄 energy_2h_aggregated.duckdb (données traitées)
└── 📂 engineering/
    ├── 📄 data_processor.py (processeur principal)
    ├── 📄 data_generator.py (gestion des trous)
    ├── 📄 data_checker.py (vérification)
    ├── 📄 pipeline_runner.py (orchestration)
    └── 📄 auto_update.py (mise à jour automatique)
```

## ⚠️ Problèmes connus

- **Formule d'énergie incorrecte** : `Global_active_power × 0.048` (pour données minute)
- **Résultat** : ~3.8 kWh/j (trop bas pour un foyer de 3 personnes)
- **Données** : Fréquence minute par minute (pas optimale)

## 🚀 Utilisation

```bash
# Exécuter le processeur
python data_kaggle/engineering/data_processor.py

# Mise à jour automatique
python -c "from data_kaggle.engineering.auto_update import AutoDataUpdater; AutoDataUpdater().run_complete_update()"
```

## 📊 Résultats

- **Total** : ~2,776 kWh sur 2 ans
- **Journalier** : ~3.8 kWh/j
- **Écart** : -68% de la cible métier (12 kWh/j)

## 🔄 Migration

Cette pipeline est **dépréciée** en faveur de `data_genere/` qui utilise des données fictives optimisées.









