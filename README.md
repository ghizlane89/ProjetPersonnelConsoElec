# ⚡ Energy Agent - Chatbot de Consommation Électrique

## 📋 Vue d'Ensemble

**Energy Agent** est une application Streamlit qui analyse et prédit la consommation électrique d'un ménage. Elle utilise l'IA (Google Gemini 1.5 Flash) pour répondre aux questions en français en moins de 5 secondes.

## 🏗️ Architecture

L'application suit une architecture en 4 couches :
- **Data Engineering** : Traitement des données avec Polars + Pandas
- **Intelligence Layer** : Planification avec Google Gemini
- **MCP Execution** : Agents pour exécuter les actions
- **Orchestration** : Coordination avec LangGraph

## 📁 Structure du Projet

```
energy-agent/
├── .env                          # Variables d'environnement (API Gemini)
├── .gitignore                    # Fichiers ignorés par Git
├── environment.yml               # Configuration Conda
├── app.py                        # Application Streamlit principale
├── data_processor.py             # Script de traitement des données
│
├── data/                         # 📊 Données source et traitées
│   ├── raw/                      # Données brutes
│   │   ├── household.csv         # Données source originales
│   │   └── household.txt         # Données source supplémentaires
│   └── processed/                # Données traitées
│       └── energy_2h_aggregated.duckdb  # Base de données optimisée
│
├── data_pipeline/                # COUCHE 1 - Gestion des données
│   ├── data_loader.py           # Charge depuis DuckDB
│   └── data_validator.py        # Valide les données
│
├── llm_planner/                  # COUCHE 2 - Intelligence
│   └── optimized_planner.py      # Planificateur intelligent
│
├── mcp_server/                   # COUCHE 3 - Exécution
│   └── simple_mcp_server.py      # Agents MCP
│
├── orchestration/                # COUCHE 4 - Orchestration
│   └── optimized_workflow_engine.py # Workflow LangGraph
│
├── tests/                        # Tests techniques par blocs
│   ├── test_data_processor.py   # BLOC 1
│   ├── test_intelligence_layer.py # BLOC 2
│   ├── test_mcp_execution.py    # BLOC 3
│   └── test_full_workflow.py    # BLOC 4
│
├── tests_uat/                    # Tests utilisateur (UAT)
│   ├── test_46_questions.py     # Tests des 46 questions
│   ├── test_interface.py        # Tests interface
│   └── test_user_experience.py  # Tests UX
│
├── config/                       # Configuration
│   └── requirements.txt          # Dépendances pip
│
├── docs/                         # Documentation
│   └── architecture_technique_finale.md # Architecture détaillée
│
└── docker-compose.yml            # Déploiement Docker
```

## 🚀 Installation

### 1. Configuration de l'environnement Conda
```bash
# Créer l'environnement
conda env create -f environment.yml

# Activer l'environnement
conda activate energy-agent
```

### 2. Configuration des variables d'environnement
```bash
# Copier le fichier .env.example et ajouter votre clé API Gemini
cp .env.example .env
# Éditer .env avec votre clé API Gemini
```

### 3. Traitement initial des données
```bash
# Traiter les données source (une seule fois)
python data_processor.py
```

### 4. Lancement de l'application
```bash
# Démarrer l'application Streamlit
streamlit run app.py
```

### 5. Déploiement avec Docker (optionnel)
```bash
# Construire et démarrer avec Docker Compose
docker-compose up --build

# Ou construire l'image Docker
docker build -t energy-agent .
docker run -p 8501:8501 energy-agent
```

## 🧪 Tests

### Tests Techniques (par blocs)
```bash
# Tests de la couche Data Engineering
python -m pytest tests/test_data_processor.py

# Tests de la couche Intelligence
python -m pytest tests/test_intelligence_layer.py

# Tests de la couche MCP Execution
python -m pytest tests/test_mcp_execution.py

# Tests du workflow complet
python -m pytest tests/test_full_workflow.py
```

### Tests Utilisateur (UAT)
```bash
# Tests des 46 questions du cahier des charges
python tests_uat/test_46_questions.py

# Tests de l'interface
python tests_uat/test_interface.py

# Tests d'expérience utilisateur
python tests_uat/test_user_experience.py
```

## 📊 Données

- **Source** : Dataset Kaggle "Household Electric Power Consumption"
- **Période** : 16/12/2023 à 10/10/2025
- **Granularité** : Données à la minute, agrégées en tranches de 2h
- **Taille** : 955,117 lignes → 11,000 lignes après agrégation

## 🎯 Fonctionnalités

- **Chatbot intelligent** : Réponses en français en <5s
- **Visualisations interactives** : Graphiques Plotly
- **Prévisions** : Modèle Prophet pour les prédictions
- **Analyse de coûts** : Tarif fixe €0.20/kWh
- **Interface moderne** : Design Streamlit professionnel

## 🔧 Technologies

- **Frontend** : Streamlit
- **IA** : Google Gemini 1.5 Flash API
- **Données** : Polars + Pandas + DuckDB
- **ML** : Prophet (prévisions)
- **Orchestration** : LangGraph
- **Visualisation** : Plotly

## 📈 Performance

- **SLA** : Réponses chatbot <5 secondes
- **Chargement** : Graphiques <2 secondes
- **Traitement** : Agrégation données <20 secondes (une seule fois)

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 Support

Pour toute question ou problème, ouvrez une issue sur GitHub.
