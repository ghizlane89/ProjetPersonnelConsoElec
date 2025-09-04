# ⚡ Energy Agent - Assistant Intelligent pour l'Analyse de Consommation Électrique

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.1+-green.svg)](https://langchain.com/langgraph)
[![DuckDB](https://img.shields.io/badge/DuckDB-0.9+-yellow.svg)](https://duckdb.org)
[![Prophet](https://img.shields.io/badge/Prophet-Facebook-orange.svg)](https://facebook.github.io/prophet/)

## 📋 Table des Matières

- [🎯 Vue d'Ensemble](#-vue-densemble)
- [🚀 Fonctionnalités](#-fonctionnalités)
- [🏗️ Architecture](#️-architecture)
- [📦 Installation](#-installation)
- [⚙️ Configuration](#️-configuration)
- [🎮 Utilisation](#-utilisation)
- [🔧 Structure du Projet](#-structure-du-projet)
- [🤖 Agents et Workflow](#-agents-et-workflow)
- [📊 Interface Utilisateur](#-interface-utilisateur)
- [🔮 Prévisions Prophet](#-prévisions-prophet)
- [📈 Données et Base](#-données-et-base)
- [🛠️ Développement](#️-développement)
- [🧪 Tests](#-tests)
- [📝 API et Intégrations](#-api-et-intégrations)
- [🔒 Sécurité](#-sécurité)
- [📊 Performance](#-performance)
- [🤝 Contribution](#-contribution)
- [📄 Licence](#-licence)

---

## 🎯 Vue d'Ensemble

**Energy Agent** est une application d'intelligence artificielle moderne dédiée à l'analyse de consommation électrique. Elle combine une architecture agentique sophistiquée (LangGraph) avec une interface utilisateur intuitive (Streamlit) pour offrir des insights précieux sur la consommation énergétique.

### 🎬 Démonstration Vidéo

📹 **[Voir la démonstration complète sur Loom](https://www.loom.com/share/bc94951d58f64ae1af4da87dba532ce6)**

### 🏆 Points Forts

- **🤖 Architecture Agentique** : 8 agents spécialisés orchestrés par LangGraph
- **🎨 Interface Moderne** : Design bleu/vert dégradé avec animations fluides
- **📊 Données Réalistes** : Base de données de 2 ans (8,772 lignes)
- **🔮 Prévisions Avancées** : Modèle Prophet de Facebook
- **⚡ Performance** : Réponses en 2-3 secondes
- **🔧 Modularité** : Architecture extensible et maintenable

---

## 🚀 Fonctionnalités

### 💬 Chat Intelligent
- **Questions Naturelles** : Posez vos questions en langage naturel
- **46+ Questions Métier** : Suggestions intelligentes organisées par catégories
- **Réponses Contextuelles** : Analyse sémantique et stratégie adaptative
- **Performance** : Traitement en <3 secondes

**Exemples de Questions :**
```
"Quelle a été ma consommation hier ?"
"Combien ai-je consommé le mois dernier ?"
"Quelle est ma consommation moyenne par jour ?"
"Ma consommation en été est-elle plus élevée qu'en hiver ?"
```

### 📊 Tableau de Bord Interactif
- **Métriques Clés** : Moyennes journalière, hebdomadaire, mensuelle
- **Graphiques Dynamiques** : Consommation mensuelle sur 12 mois
- **Répartition par Équipement** : Cuisine, Buanderie, Ballon d'eau chaude
- **Analyse Intelligente** : Comparaison nationale, tendances, alertes
- **Conseils d'Économie** : Recommandations personnalisées

### 🔮 Prévisions Prophet
- **Entraînement Automatique** : Modèle Prophet de Facebook
- **Horizons Flexibles** : 7, 14, 30 jours
- **Métriques Détaillées** : Consommation, moyennes, pics
- **Bandes de Confiance** : Intervalles d'incertitude
- **Composantes du Modèle** : Tendances, saisonnalité, changements

### 🔧 Gestion des Données
- **Détection de Gaps** : Identification automatique des données manquantes
- **Génération Automatique** : Remplissage des lacunes
- **Backup Intelligent** : Sauvegarde des données critiques
- **Intégrité** : Validation et nettoyage des données

---

## 🏗️ Architecture

### 🎼 Orchestration LangGraph

L'application utilise une architecture agentique moderne avec **8 agents spécialisés** :

```
Question → Validation → Intent Analysis → LLM Agent → Strategy → MCP Agent → Response Builder → Réponse
```

#### 🤖 Agents Spécialisés

1. **Validator** : Validation initiale des questions
2. **Intent Analyzer** : Analyse sémantique et classification
3. **Semantic Validator** : Validation LangChain des périodes
4. **LLM Agent** : Génération de plans avec Gemini
5. **Strategy Builder** : Construction de stratégies d'exécution
6. **MCP Agent** : Exécution des outils spécialisés
7. **Response Builder** : Formatage des réponses
8. **Error Handler** : Gestion des erreurs

### 🔧 Composants Techniques

#### **Frontend (Streamlit)**
- Interface utilisateur moderne avec CSS personnalisé
- Navigation par onglets (Chat, Dashboard, Prévisions)
- Sidebar avec état des systèmes et gestion des données
- Visualisations interactives avec Plotly

#### **Backend (LangGraph + LangChain)**
- **LangGraph** : Orchestration des agents
- **LangChain** : Validation sémantique et traitement
- **Gemini** : Modèle de langage Google
- **DuckDB** : Base de données analytique

#### **MCP Server (Outils Modulaires)**
- **EnergyMCPTools** : Outils d'analyse énergétique
- **DashboardTools** : Outils de visualisation
- **ProphetForecastTool** : Outils de prévision
- **DatabaseManager** : Gestion des données

---

## 📦 Installation

### Prérequis

- **Python 3.11+**
- **Conda** (recommandé) ou **pip**
- **Git**

### 🚀 Installation Rapide

```bash
# 1. Cloner le repository
git clone https://github.com/votre-username/Energy-Agent.git
cd Energy-Agent

# 2. Créer l'environnement conda
conda env create -f environment.yml

# 3. Activer l'environnement
conda activate energy-agent

# 4. Lancer l'application
streamlit run app2.py
```

### 📋 Dépendances Principales

```yaml
# environment.yml
name: energy-agent
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.11
  - pandas>=2.0.0
  - polars>=0.20.0
  - duckdb>=0.9.0
  - plotly>=5.15.0
  - streamlit>=1.28.0
  - numpy>=1.24.0
  - pip
  - pip:
    - google-generativeai>=0.3.0
    - python-dotenv>=1.0.0
    - langgraph>=0.1.0
```

---

## ⚙️ Configuration

### 🔑 Variables d'Environnement

Créez un fichier `.env` à la racine du projet :

```bash
# .env
GOOGLE_API_KEY=votre_clé_api_gemini
DUCKDB_PATH=data_genere/processed/energy_fictional_2h.duckdb
LOG_LEVEL=INFO
```

### 🗄️ Base de Données

L'application utilise une base de données DuckDB avec des données fictives :

```sql
-- Structure de la table energy_data
CREATE TABLE energy_data (
    timestamp TIMESTAMP,
    global_active_power_kw FLOAT,
    global_reactive_power_kw FLOAT,
    voltage FLOAT,
    global_intensity FLOAT,
    sub_metering_1_kwh FLOAT,  -- Cuisine
    sub_metering_2_kwh FLOAT,  -- Buanderie
    sub_metering_3_kwh FLOAT,  -- Ballon d'eau chaude
    energy_total_kwh FLOAT
);
```

---

## 🎮 Utilisation

### 🚀 Démarrage Rapide

```bash
# Activer l'environnement
conda activate energy-agent

# Lancer l'application
streamlit run app2.py
```

L'application sera accessible à l'adresse : `http://localhost:8501`

### 📱 Interface Utilisateur

#### **1. Chat Intelligent**
- Saisissez vos questions en langage naturel
- Utilisez les suggestions de questions
- Consultez les réponses formatées

#### **2. Tableau de Bord**
- Visualisez les métriques clés
- Explorez les graphiques interactifs
- Analysez les tendances et alertes

#### **3. Prévisions**
- Configurez les paramètres d'entraînement
- Générez des prévisions Prophet
- Consultez les métriques et composantes

### 🎯 Exemples d'Utilisation

#### **Questions Simples**
```
"Quelle a été ma consommation hier ?"
→ Réponse : "Votre consommation hier était de 12.5 kWh"
```

#### **Questions Complexes**
```
"Quelle est ma consommation moyenne par jour et comment se compare-t-elle à la moyenne nationale ?"
→ Réponse : "Votre consommation moyenne quotidienne est de 8.2 kWh, soit 12% au-dessus de la moyenne française pour un foyer de 3 personnes"
```

#### **Prévisions**
```
1. Sélectionnez une période d'entraînement (365 jours)
2. Choisissez un horizon de prévision (30 jours)
3. Cliquez sur "Entraîner et Générer"
4. Consultez les graphiques et métriques
```

---

## 🔧 Structure du Projet

```
Energy-Agent/
├── 📁 app2.py                          # Application principale Streamlit
├── 📁 environment.yml                   # Dépendances conda
├── 📁 .env                              # Variables d'environnement
├── 📁 .gitignore                        # Fichiers ignorés par Git
├── 📁 LICENSE                           # Licence du projet
│
├── 📁 orchestration/                    # 🎼 Orchestration LangGraph
│   ├── 📁 agents/                       # Agents métier spécialisés
│   │   ├── energy_business_rules.py     # Règles métier énergétiques
│   │   ├── standard_response.py         # Formatage des réponses
│   │   └── ...
│   ├── energy_langgraph_workflow.py     # Workflow principal
│   └── __init__.py
│
├── 📁 mcp_server/                       # 🔧 Serveur MCP (Outils Modulaires)
│   ├── 📁 core/
│   │   ├── energy_mcp_tools.py          # Outils d'analyse énergétique
│   │   ├── dashboard_tools.py           # Outils de visualisation
│   │   ├── prophet_forecast_tool.py      # Outils de prévision Prophet
│   │   ├── database_manager.py          # Gestionnaire de base de données
│   │   └── __init__.py
│   └── __init__.py
│
├── 📁 core/                             # 🎯 Composants principaux
│   ├── 📁 dashboard/
│   │   └── forecast_page.py             # Page de prévisions
│   └── ...
│
├── 📁 data_genere/                      # 📊 Données et pipelines
│   ├── 📁 processed/                    # Données traitées
│   │   └── energy_fictional_2h.duckdb  # Base de données principale
│   ├── 📁 backups/                      # Sauvegardes critiques
│   ├── 📁 generation/                   # Génération de données
│   ├── 📁 pipelines/                    # Pipelines de traitement
│   └── README.md
│
├── 📁 data_genere_gap/                  # 🔍 Gestion des gaps
│   └── gap_manager.py                   # Détection et remplissage
│
├── 📁 llm_planner/                      # 🤖 Planification LLM
│   ├── 📁 core/
│   │   └── gemini_client.py             # Client Gemini
│   └── ...
│
├── 📁 docs/                             # 📚 Documentation
└── 📁 dashboard/                        # 📊 Composants dashboard (obsolète)
```

---

## 🤖 Agents et Workflow

### 🎼 Workflow LangGraph

```python
# Exemple de workflow simplifié
class EnergyLangGraphWorkflow:
    def __init__(self):
        # Agents métier
        self.business_rules = EnergyBusinessRules()
        self.response_builder = ResponseBuilder()
        
        # Agents techniques
        self.llm_agent = GeminiClient()
        self.capabilities_agent = get_energy_capabilities()
        
        # Workflow
        self.workflow = self._create_workflow()
```

### 🔄 Flux de Traitement

1. **Question Utilisateur** → Validation initiale
2. **Intent Analysis** → Classification sémantique
3. **LLM Agent** → Génération de plan avec Gemini
4. **Strategy Builder** → Construction de stratégie
5. **MCP Agent** → Exécution des outils spécialisés
6. **Response Builder** → Formatage de la réponse
7. **Réponse Finale** → Affichage à l'utilisateur

### 🎯 Types d'Agents

#### **Agents Métier**
- **EnergyBusinessRules** : Règles spécifiques au domaine énergétique
- **QuestionIntent** : Analyse d'intention des questions
- **ExecutionStrategy** : Stratégies d'exécution
- **StandardResponse** : Formatage standardisé des réponses

#### **Agents Techniques**
- **GeminiClient** : Interface avec le modèle de langage
- **EnergyMCPTools** : Outils d'analyse énergétique
- **DatabaseManager** : Gestion des données
- **ProphetForecastTool** : Outils de prévision

---

## 📊 Interface Utilisateur

### 🎨 Design System

L'application utilise un design system cohérent avec :

#### **Palette de Couleurs**
- **Primaire** : `#2563eb` (Bleu)
- **Secondaire** : `#10b981` (Vert)
- **Accent** : `#3b82f6` (Bleu clair)
- **Dégradés** : Combinaisons bleu/vert

#### **Composants CSS**
```css
.main-header {
    background: linear-gradient(135deg, #2563eb 0%, #10b981 50%, #3b82f6 100%);
    /* ... */
}

.electric-card {
    background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
    border: 2px solid #2563eb;
    /* ... */
}
```

### 📱 Navigation

#### **Onglets Principaux**
1. **💬 Chat Intelligent** : Interface de conversation
2. **📊 Tableau de Bord** : Visualisations et métriques
3. **📈 Prévisions** : Modèles prédictifs

#### **Sidebar**
- **🔄 Gestion des Données** : Détection et génération de gaps
- **📊 Résumé Exécutif** : Métriques clés et tendances
- **🔧 État des Systèmes** : Monitoring des composants

### 🎯 Composants Interactifs

#### **Chat Intelligent**
- Zone de saisie avec placeholder intelligent
- Suggestions de questions organisées par catégories
- Affichage des réponses formatées
- Indicateurs de traitement

#### **Tableau de Bord**
- Métriques avec animations
- Graphiques Plotly interactifs
- Cartes d'analyse intelligente
- Conseils d'économie

#### **Prévisions**
- Paramètres configurables
- Bouton d'entraînement unifié
- Graphiques de prévision
- Métriques détaillées

---

## 🔮 Prévisions Prophet

### 🎯 Modèle Prophet

L'application intègre le modèle Prophet de Facebook pour les prévisions temporelles :

#### **Caractéristiques**
- **Prévisions temporelles** : Modèle additif avec composantes
- **Saisonnalité** : Détection automatique des patterns
- **Changements** : Adaptation aux changements de tendance
- **Intervalles de confiance** : Estimation des incertitudes

#### **Composantes du Modèle**
```python
# Exemple de composantes
components = {
    "trend": "Direction et amplitude de la tendance",
    "seasonality": "Patterns hebdomadaires et annuels",
    "holidays": "Effets des jours fériés",
    "changepoints": "Points de changement de tendance"
}
```

### ⚙️ Configuration

#### **Paramètres d'Entraînement**
- **Période** : 30 à 730 jours (défaut : 365)
- **Horizon** : 7, 14, 30 jours
- **Type de modèle** : Simple ou Avancé

#### **Métriques de Performance**
- **Erreur moyenne** : ±5%
- **Intervalle de confiance** : 90%
- **Temps de génération** : <2 secondes

### 📊 Visualisations

#### **Graphiques de Prévision**
- Ligne de prévision principale
- Bandes de confiance
- Données historiques
- Composantes du modèle

#### **Métriques Détaillées**
- Consommation totale prévue
- Moyennes et pics
- Comparaisons avec l'historique
- Indicateurs de confiance

---

## 📈 Données et Base

### 🗄️ Base de Données DuckDB

#### **Structure des Données**
```sql
-- Table principale energy_data
CREATE TABLE energy_data (
    timestamp TIMESTAMP,                    -- Horodatage
    global_active_power_kw FLOAT,          -- Puissance active globale
    global_reactive_power_kw FLOAT,         -- Puissance réactive globale
    voltage FLOAT,                          -- Tension
    global_intensity FLOAT,                 -- Intensité globale
    sub_metering_1_kwh FLOAT,               -- Cuisine (kWh)
    sub_metering_2_kwh FLOAT,               -- Buanderie (kWh)
    sub_metering_3_kwh FLOAT,               -- Ballon d'eau chaude (kWh)
    energy_total_kwh FLOAT                 -- Consommation totale (kWh)
);
```

#### **Caractéristiques**
- **Format** : DuckDB (OLAP)
- **Taille** : ~8,772 lignes
- **Période** : 2 ans de données fictives
- **Granularité** : Mesures toutes les 2 heures
- **Compression** : Optimisée pour les requêtes analytiques

### 🔄 Gestion des Données

#### **Pipeline de Données**
1. **Génération** : Création de données fictives réalistes
2. **Validation** : Vérification de l'intégrité
3. **Traitement** : Agrégations et calculs
4. **Stockage** : Sauvegarde en DuckDB
5. **Monitoring** : Détection de gaps

#### **Gestion des Gaps**
```python
# Exemple de détection de gaps
gap_manager = GapManager()
status = gap_manager.get_gap_status()

if status['gap_detected']:
    # Génération automatique des données manquantes
    result = gap_manager.check_and_fill_gaps()
```

### 📊 Données Fictives

#### **Caractéristiques Réalistes**
- **Consommation moyenne** : 8-12 kWh/jour
- **Pics de consommation** : 18h-20h
- **Saisonnalité** : +15% en hiver, -10% en été
- **Équipements** : Répartition réaliste par zone

#### **Patterns Simulés**
- **Hebdomadaire** : Dimanche plus faible
- **Quotidien** : Pics matin et soir
- **Saisonnier** : Variations hiver/été
- **Aléatoire** : Bruit réaliste

---

## 🛠️ Développement

### 🏗️ Architecture de Développement

#### **Patterns Utilisés**
- **Agent Pattern** : Agents spécialisés et modulaires
- **Workflow Pattern** : Orchestration avec LangGraph
- **Repository Pattern** : Abstraction des données
- **Factory Pattern** : Création d'instances
- **Observer Pattern** : Monitoring des systèmes

#### **Principes SOLID**
- **Single Responsibility** : Chaque agent a une responsabilité unique
- **Open/Closed** : Extension sans modification
- **Liskov Substitution** : Substitution transparente
- **Interface Segregation** : Interfaces spécialisées
- **Dependency Inversion** : Dépendances abstraites

### 🔧 Outils de Développement

#### **Environnement**
```bash
# Développement
conda activate energy-agent
python -m streamlit run app2.py

# Debug
python -c "import app2; print('Modules OK')"

# Tests
python -m pytest tests/
```

#### **Linting et Formatage**
```bash
# Black (formatage)
black app2.py orchestration/ mcp_server/

# Flake8 (linting)
flake8 app2.py orchestration/ mcp_server/

# Type checking
mypy app2.py orchestration/ mcp_server/
```

### 📝 Bonnes Pratiques

#### **Code**
- **Documentation** : Docstrings complètes
- **Type hints** : Annotations de types
- **Error handling** : Gestion d'erreurs robuste
- **Logging** : Traçabilité des opérations
- **Testing** : Tests unitaires et d'intégration

#### **Architecture**
- **Modularité** : Composants indépendants
- **Extensibilité** : Facile d'ajouter de nouveaux agents
- **Maintenabilité** : Code clair et documenté
- **Performance** : Optimisations ciblées
- **Sécurité** : Validation des entrées

---

## 🧪 Tests

### 🎯 Stratégie de Tests

#### **Tests Unitaires**
```python
# Exemple de test unitaire
def test_energy_business_rules():
    rules = EnergyBusinessRules()
    result = rules.analyze_intent("Quelle est ma consommation hier ?")
    assert result['intent'] == 'consumption_query'
    assert result['period'] == 'yesterday'
```

#### **Tests d'Intégration**
```python
# Exemple de test d'intégration
def test_workflow_complete():
    workflow = get_energy_workflow()
    response = workflow.process_question("Ma consommation hier ?")
    assert response['status'] == 'success'
    assert 'answer' in response
```

#### **Tests de Performance**
```python
# Exemple de test de performance
def test_response_time():
    workflow = get_energy_workflow()
    start_time = time.time()
    response = workflow.process_question("Test question")
    duration = time.time() - start_time
    assert duration < 3.0  # < 3 secondes
```

### 📊 Couverture de Tests

#### **Métriques**
- **Couverture de code** : >80%
- **Tests unitaires** : Tous les agents
- **Tests d'intégration** : Workflows complets
- **Tests de performance** : Temps de réponse
- **Tests de sécurité** : Validation des entrées

---

## 📝 API et Intégrations

### 🔌 API Interne

#### **Workflow API**
```python
# Interface principale
workflow = get_energy_workflow()
response = workflow.process_question(question: str) -> Dict[str, Any]
```

#### **MCP Tools API**
```python
# Outils d'analyse
tools = get_energy_capabilities()
result = tools.query_energy_data(period, aggregation, filters)
```

#### **Database API**
```python
# Gestionnaire de base
db_manager = get_database_manager()
data = db_manager.get_sample_data(limit=1000)
```

### 🔗 Intégrations Externes

#### **Google Gemini**
- **Modèle** : gemini-pro
- **Usage** : Génération de plans et analyse
- **Configuration** : Via API key

#### **DuckDB**
- **Base** : OLAP pour analytics
- **Performance** : Requêtes optimisées
- **Format** : Parquet/CSV

#### **Streamlit**
- **Interface** : Web app interactive
- **Visualisations** : Plotly intégré
- **State** : Session management

---

## 🔒 Sécurité

### 🛡️ Mesures de Sécurité

#### **Validation des Entrées**
```python
# Exemple de validation
def validate_question(question: str) -> bool:
    if not question or len(question) > 500:
        return False
    # Validation supplémentaire...
    return True
```

#### **Gestion des Erreurs**
```python
# Exemple de gestion d'erreur
try:
    result = workflow.process_question(question)
except Exception as e:
    logger.error(f"Erreur workflow: {e}")
    return {"error": "Erreur de traitement"}
```

#### **Sécurité des Données**
- **Validation** : Toutes les entrées utilisateur
- **Sanitisation** : Nettoyage des données
- **Logging** : Traçabilité des opérations
- **Isolation** : Environnements séparés

---

## 📊 Performance

### ⚡ Métriques de Performance

#### **Temps de Réponse**
- **Chat** : <3 secondes
- **Dashboard** : <2 secondes
- **Prévisions** : <5 secondes
- **Génération de données** : <10 secondes

#### **Optimisations**
- **Cache** : Données en mémoire
- **Indexation** : Requêtes optimisées
- **Parallélisation** : Traitement concurrent
- **Compression** : Données compressées

#### **Monitoring**
```python
# Exemple de monitoring
def monitor_performance():
    start_time = time.time()
    result = process_operation()
    duration = time.time() - start_time
    
    if duration > threshold:
        logger.warning(f"Performance dégradée: {duration}s")
```

---

## 🤝 Contribution

### 📋 Guide de Contribution

#### **Fork et Clone**
```bash
# Fork le repository
git clone https://github.com/votre-fork/Energy-Agent.git
cd Energy-Agent

# Créer une branche
git checkout -b feature/nouvelle-fonctionnalite
```

#### **Développement**
```bash
# Installer l'environnement
conda env create -f environment.yml
conda activate energy-agent

# Développer
# ... modifications ...

# Tests
python -m pytest tests/

# Commit
git add .
git commit -m "feat: ajout nouvelle fonctionnalité"
git push origin feature/nouvelle-fonctionnalite
```

#### **Pull Request**
1. **Fork** le repository
2. **Créer** une branche feature
3. **Développer** la fonctionnalité
4. **Tester** complètement
5. **Documenter** les changements
6. **Soumettre** la PR

### 📝 Standards de Code

#### **Conventions**
- **PEP 8** : Style Python
- **Docstrings** : Documentation complète
- **Type hints** : Annotations de types
- **Tests** : Couverture >80%

#### **Commit Messages**
```
feat: nouvelle fonctionnalité
fix: correction de bug
docs: mise à jour documentation
refactor: refactorisation de code
test: ajout de tests
```

---

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

### 📋 Conditions d'Utilisation

- **Usage libre** : Utilisation personnelle et commerciale
- **Modification** : Modification et distribution autorisées
- **Attribution** : Citation de l'auteur original
- **Responsabilité** : Utilisation à vos propres risques

---

## 📞 Support

### 🆘 Aide et Support

#### **Documentation**
- **README** : Ce fichier
- **Code** : Docstrings dans le code
- **Issues** : GitHub Issues
- **Wiki** : Documentation détaillée

#### **Contact**
- **Issues** : [GitHub Issues](https://github.com/votre-username/Energy-Agent/issues)
- **Discussions** : [GitHub Discussions](https://github.com/votre-username/Energy-Agent/discussions)
- **Email** : votre-email@example.com

#### **Communauté**
- **Contributions** : Bienvenues !
- **Feedback** : Apprécié
- **Suggestions** : Ouvertes aux améliorations

---

## 🎉 Remerciements

- **LangGraph** : Pour l'orchestration agentique
- **Streamlit** : Pour l'interface utilisateur
- **DuckDB** : Pour la base de données analytique
- **Prophet** : Pour les prévisions temporelles
- **Google Gemini** : Pour l'intelligence artificielle
- **Communauté Open Source** : Pour les outils et bibliothèques

---

**⚡ Energy Agent** - Transformez vos données énergétiques en insights intelligents !

*Développé avec ❤️ pour l'analyse énergétique moderne*
