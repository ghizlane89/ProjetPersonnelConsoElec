# 🔧 Data Générée - Gestion des Gaps

## 📋 Description

Ce répertoire contient les scripts pour gérer les données manquantes (gaps) dans le dataset fictif de consommation électrique.

## 🎯 Objectifs

- **Détection automatique** des gaps dans les données
- **Génération de données** pour combler les trous
- **Mise à jour continue** du dataset
- **Cohérence temporelle** (mesures toutes les 2h)

## 📁 Structure

```
data_genere_gap/
├── README.md                    # Documentation
├── gap_detector.py              # Détection des gaps
├── gap_filler.py               # Génération pour combler gaps
├── continuous_updater.py        # Mise à jour continue
└── utils/                       # Utilitaires
    ├── time_utils.py            # Gestion du temps
    └── validation_utils.py      # Validation des données
```

## 🚀 Utilisation

### Détecter les gaps
```bash
python gap_detector.py
```

### Combler les gaps
```bash
python gap_filler.py --start-date "2025-09-01" --end-date "2025-09-03"
```

### Mise à jour continue
```bash
python continuous_updater.py
```

## ⚙️ Configuration

Le système respecte les mêmes contraintes que le générateur principal :
- **Période** : Données toutes les 2h
- **Contraintes physiques** : P ≤ U×I/1000, PF ∈ [0.94, 0.99]
- **Cohérence temporelle** : Continuité avec les données existantes








