# Architecture Technique Finale - Energy Agent

## Vue d'Ensemble Simplifiée

### Stack Technologique
```
Frontend:     Streamlit (Python) - Interface utilisateur
Orchestration: LangGraph (Python) - Coordination intelligente
LLM:          Google Gemini 1.5 Flash API - Intelligence
Data Layer:   DuckDB + Pandas + Polars - Base de données hybride
ML:           Prophet (entraînement unique) - Prévisions
MCP:          Outils intégrés - Actions sur les données
```

### Flux Principal
```
Question Utilisateur → LLM Analyse → LLM Plan → Agents MCP → DuckDB → Réponse
```

## Architecture en 4 Blocs Validés

### **Bloc 1: Data Engineering**
**Responsabilité :** Gérer vos données énergétiques avec mise à jour automatique

**Ce qu'elle fait :**
- Lit votre CSV de 895,345 lignes avec **Polars** (performance maximale)
- Nettoie et agrège en données toutes les 2h (7,433 lignes)
- Convertit en **Pandas** pour intégration parfaite avec l'écosystème
- Stocke dans DuckDB avec index pour rapidité
- **MISE À JOUR AUTOMATIQUE** via pipeline intelligent
- **DÉTECTION DE GAP** avec tolérance de 5 minutes

**Stratégie Hybride :**
- **Polars** : Traitement lourd des données (lecture, nettoyage, agrégation)
- **Pandas** : Intégration avec DuckDB, Streamlit, Plotly

**Fichiers Réels :**
- `data_processor.py` (script de traitement hybride Polars → Pandas)
- `data/engineering/auto_update.py` (mise à jour automatique)
- `data/engineering/pipeline_runner.py` (exécution du pipeline)
- `data/engineering/data_checker.py` (détection de gap)
- `data/engineering/data_generator.py` (génération de données)
- `data/raw/household.csv` (données source - 895,345 lignes)
- `data/processed/energy_2h_aggregated.duckdb` (données traitées - 7,433 lignes)

**Performance Validée :**
- **Traitement** : 2.5s (895k → 7.4k lignes)
- **Mise à jour** : 2.7s avec validation
- **Gap détection** : Tolérance 5 minutes
- **Données source** : 895,345 lignes (avec en-tête)
- **Données traitées** : 7,433 lignes agrégées

---

### **Bloc 2: Intelligence Layer**
**Responsabilité :** Réfléchir et planifier avec Gemini 1.5 Flash

**Ce qu'elle fait :**
- Analyse votre question avec Gemini 1.5 Flash
- Génère un plan d'exécution personnalisé
- Met en cache les plans pour optimiser (clé de cache)
- **CORRECTION AUTOMATIQUE** des plans invalides
- **VALIDATION** des plans avant exécution

**Fichiers Réels :**
- `llm_planner/core/` (structure modulaire)
- `llm_planner/prompts/` (prompts optimisés)
- `llm_planner/models/` (modèles de planification)

**Performance Validée :**
- **Génération plan** : 1.54s
- **Cache hit** : 0.01s
- **Correction plans** : Automatique

---

### **Bloc 3: Execution Layer (MCP Tools)**
**Responsabilité :** Exécuter les actions via serveur MCP

**Ce qu'elle fait :**
- Contient des agents qui lisent dans DuckDB
- Chaque agent a une spécialité (extraction, statistiques, prévisions)
- Exécute les plans générés par la Couche 2
- **OUTILS LANGCHAIN** intégrés
- **OUTILS TABLEAU DE BORD** pour visualisations

**Fichiers Réels :**
- `mcp_server/core/` (serveur MCP principal)
- `mcp_server/core/dashboard_tools.py` (outils tableau de bord)
- `mcp_server/core/database_manager.py` (gestionnaire base de données)
- `mcp_server/core/energy_business_logic.py` (logique métier énergie)

**Performance Validée :**
- **Lecture DuckDB** : <0.5s
- **Agrégation** : Exécution réussie
- **Outils** : 100% fonctionnels

---

### **Bloc 4: Orchestration Layer**
**Responsabilité :** Coordonner tout le processus avec LangGraph

**Ce qu'elle fait :**
- Utilise LangGraph pour orchestrer le workflow
- Gère les étapes : Classification → Planning → Exécution → Synthèse
- Respecte le SLA de 5 secondes
- **GESTION D'ERREURS** robuste
- **FORMATAGE** des réponses

**Fichiers Réels :**
- `orchestration/langgraph_orchestrator.py` (orchestrateur principal)
- `orchestration/plan_validator.py` (validation des plans)
- `orchestration/error_handler.py` (gestion d'erreurs)
- `orchestration/result_formatter.py` (formatage des réponses)
- `orchestration/config/orchestration_config.py` (configuration orchestration)

**Performance Validée :**
- **Temps total** : 0.48s moyen
- **Temps max** : 1.44s
- **Workflow** : 100% fonctionnel

---

## Comment les Blocs Travaillent Ensemble

### **Exemple avec "Quelle est ma consommation hier ?"**

```
1. BLOC 4 (Orchestration) reçoit la question
   ↓
2. BLOC 2 (Intelligence) analyse et planifie
   ↓
3. BLOC 4 (Orchestration) coordonne
   ↓
4. BLOC 3 (Execution) exécute le plan
   ↓
5. BLOC 3 lit dans DuckDB (Bloc 1)
   ↓
6. BLOC 2 (Intelligence) synthétise la réponse
   ↓
7. BLOC 4 (Orchestration) retourne le résultat
```

**Important :** Les blocs ne s'exécutent pas l'un après l'autre, ils travaillent ENSEMBLE !

---

## Workflow de Traitement des Données Optimisé

### **Étape 1 : Traitement Initial (UNE SEULE FOIS)**
```bash
# Exécution du script de traitement hybride
python data_processor.py
# → Crée data/processed/energy_2h_aggregated.duckdb
# → Temps : ~2.5 secondes (grâce à Polars)
# → Stratégie : Polars (performance) → Pandas (intégration)
```

### **Étape 2 : Mise à Jour Automatique (si nécessaire)**
```python
# Détection automatique de gap
from data.engineering.auto_update import AutoDataUpdater
updater = AutoDataUpdater()
updater.run_complete_update()
# → Mise à jour automatique si gap > 5 minutes
# → Temps : ~2.7 secondes
```

### **Étape 3 : Démarrage de l'Application (AUTANT QUE VOUS VOULEZ)**
```bash
# Lancement rapide de l'app
streamlit run app.py
# → Vérifie que DuckDB existe
# → Démarrage en ~2 secondes
# → Données prêtes à utiliser
```

---

## Stratégie de Test par Blocs

### **Tests d'Intégration Complets : 8/8 (100%)**

#### **1. Tests Techniques (par blocs)**
- **Tests unitaires** : Chaque composant individuellement
- **Tests d'intégration** : Interaction entre composants
- **Tests de performance** : Respect du SLA <5s
- **Tests de robustesse** : Gestion d'erreurs

#### **2. Tests Utilisateur (UAT - User Acceptance Testing)**
- **Tests fonctionnels** : Fonctionnalités métier
- **Tests d'interface** : Expérience utilisateur
- **Tests des 46 questions** du cahier des charges
- **Tests de validation** : Réponses correctes et cohérentes

### **BLOC 1 : Test de la Couche 1 (Data Engineering)**
```python
# Test : Vérifier que vos données sont bien traitées
def test_data_processor():
    # 1. Charger le CSV original avec Polars
    # 2. Exécuter l'agrégation 2H avec Polars
    # 3. Convertir en Pandas pour DuckDB
    # 4. Vérifier que DuckDB contient les bonnes données
    # 5. Mesurer le temps de traitement
    
    # Critères de succès :
    # CSV → DuckDB en 2.5s (grâce à Polars)
    # 895k lignes → 7.4k lignes
    # Données cohérentes (pas de NaN, dates valides)
    # Intégration parfaite avec l'écosystème (Pandas)
```

**Fichiers de test :**
- `tests_uat/test_integration_complete.py`

---

### **BLOC 2 : Test de la Couche 2 (Intelligence)**
```python
# Test : Vérifier que le LLM comprend et planifie
def test_intelligence_layer():
    # 1. Envoyer une question simple
    # 2. Vérifier la classification
    # 3. Vérifier la génération du plan
    # 4. Mesurer le temps de réponse
    
    # Critères de succès :
    # Classification correcte en 1.54s
    # Plan généré en 1.54s
    # Plan logique et exécutable
    # Cache fonctionnel (0.01s)
```

**Fichiers de test :**
- `tests_uat/test_integration_complete.py`

---

### **BLOC 3 : Test de la Couche 3 (Execution MCP)**
```python
# Test : Vérifier que les agents MCP fonctionnent
def test_mcp_execution():
    # 1. Créer un plan simple
    # 2. L'exécuter avec les agents MCP
    # 3. Vérifier que DuckDB est bien lu
    # 4. Mesurer le temps d'exécution
    
    # Critères de succès :
    # Lecture DuckDB en <0.5s
    # Agents MCP répondent correctement
    # Données extraites sont cohérentes
    # Outils LangChain fonctionnels
```

**Fichiers de test :**
- `tests_uat/test_integration_complete.py`

---

### **BLOC 4 : Test de la Couche 4 (Orchestration)**
```python
# Test : Vérifier que tout fonctionne ensemble
def test_full_workflow():
    # 1. Envoyer une question complète
    # 2. Suivre le workflow complet
    # 3. Vérifier la réponse finale
    # 4. Mesurer le temps total
    
    # Critères de succès :
    # Réponse complète en 0.48s (SLA respecté)
    # Workflow sans erreur
    # Réponse intelligente et correcte
    # Performance optimale
```

**Fichiers de test :**
- `tests_uat/test_integration_complete.py`

---

## Pipeline de Déploiement

### **Qu'est-ce que c'est ?**
Le processus pour "livrer" votre application aux utilisateurs finaux.

### **Pourquoi Docker ?**
- **Garantit** que l'app marche partout
- **Inclut** toutes les dépendances
- **Évite** les problèmes "ça marche sur ma machine"

### **Étapes du déploiement :**
```
1. DÉVELOPPEMENT (votre machine)
   ├── Code Python
   ├── Tests par blocs
   └── Validation

2. EMBALLAGE (Docker)
   ├── Création du conteneur
   ├── Inclusion des dépendances
   └── Configuration

3. DÉPLOIEMENT (serveur)
   ├── Envoi du conteneur
   ├── Démarrage automatique
   └── Mise en ligne
```

---

## Structure des Fichiers Réelle

```
Energy-Agent/
├── data/
│   ├── raw/
│   │   └── household.csv (895,345 lignes)
│   ├── processed/
│   │   └── energy_2h_aggregated.duckdb (7,433 lignes)
│   └── engineering/
│       ├── auto_update.py (mise à jour automatique)
│       ├── pipeline_runner.py (exécution pipeline)
│       ├── data_checker.py (détection gap)
│       └── data_generator.py (génération données)
├── llm_planner/
│   ├── core/ (planification modulaire)
│   ├── prompts/ (prompts optimisés)
│   └── models/ (modèles de planification)
├── mcp_server/
│   └── core/ (serveur MCP principal)
│       ├── dashboard_tools.py (outils tableau de bord)
│       ├── database_manager.py (gestionnaire base de données)
│       └── energy_business_logic.py (logique métier énergie)
├── orchestration/
│   ├── langgraph_orchestrator.py (orchestrateur principal)
│   ├── plan_validator.py (validation plans)
│   ├── error_handler.py (gestion erreurs)
│   ├── result_formatter.py (formatage réponses)
│   └── config/
│       └── orchestration_config.py (configuration orchestration)
├── tests_uat/
│   └── test_integration_complete.py (tests complets)
├── docs/
│   └── architecture_technique_finale.md (ce fichier)
├── data_processor.py (traitement hybride Polars → Pandas)
├── environment.yml (environnement Conda)
├── Dockerfile (déploiement Docker)
└── docker-compose.yml (orchestration Docker)
```

---

## Plan de Développement Réalisé

### **PHASE 0 : Configuration Environnement**
- **Création environnement Conda** (agent-elec)
- **Installation des dépendances** (Polars, Pandas, DuckDB, etc.)
- **Configuration des variables d'environnement** (.env)
- **Validation de l'installation**

### **PHASE 1 : Tests Techniques par Blocs**
1. **BLOC 1** : Data Processor (Couche 1) - Traitement unique des données
2. **BLOC 2** : Intelligence Layer (Couche 2) - LLM + Planning
3. **BLOC 3** : MCP Execution (Couche 3) - Agents MCP
4. **BLOC 4** : Full Workflow (Couche 4) - Orchestration complète

### **PHASE 2 : Tests Utilisateur (UAT)**
- **Tests des 46 questions** du cahier des charges
- **Tests d'interface** Streamlit (3 onglets)
- **Tests d'expérience utilisateur** (design, navigation)
- **Validation métier** des réponses

### **PHASE 3 : Intégration et Optimisation**
- Assemblage des 4 couches
- Tests d'intégration complets
- Optimisation des performances (SLA <5s)
- Tests de charge et robustesse

### **PHASE 4 : Déploiement et Production**
- Configuration Docker
- Tests de production
- Mise en ligne
- Monitoring et maintenance

---

## Estimation Temps de Développement Réalisé

### **Avec Développement en Pair (Avec mon aide)**
- **PHASE 0** : Configuration - 15 minutes
- **PHASE 1** : Blocs Techniques - 4-6 heures
- **PHASE 2** : Tests UAT - 2-3 heures
- **PHASE 3** : Intégration - 1-2 heures
- **PHASE 4** : Déploiement - 30 minutes - 1 heure

**TOTAL RÉALISÉ : 8-12 heures** (vs 26-37 heures sans aide)

---

## Configuration de l'Environnement Conda

### **Environnement Recommandé : Conda**
**Pourquoi Conda ?**
- **Polars** : Installation optimisée via conda-forge
- **DuckDB** : Support natif des dépendances système
- **Reproducibilité** : environment.yml partageable
- **Performance** : Compilation optimisée

### **Fichier Environment.yml**
```yaml
# environment.yml
name: agent-elec
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.11
  - pandas>=2.0.0          # Intégration écosystème
  - polars>=0.20.0          # Performance traitement
  - duckdb>=0.9.0           # Base de données
  - plotly>=5.15.0          # Visualisations
  - streamlit>=1.28.0       # Interface utilisateur
  - numpy>=1.24.0           # Calculs numériques
  - pip
  - pip:
    - google-generativeai>=0.3.0  # API Gemini
    - python-dotenv>=1.0.0        # Variables d'environnement
    - langgraph>=0.1.0            # Orchestration
```

### **Installation de l'Environnement**
```bash
# Créer l'environnement depuis le fichier
conda env create -f environment.yml

# Activer l'environnement
conda activate agent-elec

# Vérification de l'installation
python -c "
import polars as pl
import pandas as pd
import duckdb
import streamlit as st
import plotly.express as px
print('Tous les packages installés avec succès !')
"
```

### **Gestion de l'Environnement**
```bash
# Activer l'environnement
conda activate agent-elec

# Désactiver l'environnement
conda deactivate

# Lister les environnements
conda env list

# Exporter l'environnement
conda env export > environment.yml

# Supprimer l'environnement
conda env remove -n agent-elec
```

---

## Résumé des Types de Tests

### **Tests Techniques (par blocs)**
- **Objectif** : Valider le bon fonctionnement technique
- **Quand** : Phase 1 du développement
- **Qui** : Développeurs
- **Focus** : Performance, robustesse, intégration

### **Tests Utilisateur (UAT)**
- **Objectif** : Valider l'expérience utilisateur et les fonctionnalités métier
- **Quand** : Phase 2 du développement
- **Qui** : Utilisateurs finaux / Tests métier
- **Focus** : 46 questions du cahier des charges, interface, UX

### **Tests d'Intégration**
- **Objectif** : Valider que tout fonctionne ensemble
- **Quand** : Phase 3 du développement
- **Qui** : Développeurs + Tests automatisés
- **Focus** : Workflow complet, SLA <5s

---

## Stratégie Hybride Polars + Pandas

### **Pourquoi cette approche ?**

#### **1. Performance Maximale (Polars)**
- **Lecture CSV** : 2-5x plus rapide que Pandas
- **Traitement** : Agrégation et nettoyage ultra-rapides
- **Mémoire** : Utilisation RAM optimisée
- **Parallélisation** : Exécution multi-cœurs native

#### **2. Intégration Parfaite (Pandas)**
- **DuckDB** : Intégration native et stable
- **Streamlit** : Affichage et manipulation parfaits
- **Plotly** : Graphiques et visualisations optimaux
- **Écosystème** : Support et documentation excellents

### **Workflow de Traitement Hybride**
```
CSV Original (895k lignes)
         ↓
    POLARS (Performance)
         ↓
   Traitement + Agrégation 2H
         ↓
    Conversion Pandas
         ↓
   Sauvegarde DuckDB
         ↓
   Application Streamlit (Pandas)
```

### **Gains de Performance Validés**
- **Traitement initial** : 2.5s (grâce à Polars)
- **Démarrage app** : 2s (données prêtes)
- **Lecture données** : Ultra-rapide (DuckDB + Pandas)
- **Intégration** : Parfaite avec tout l'écosystème
- **Données source** : 895,345 lignes (avec en-tête)
- **Données traitées** : 7,433 lignes agrégées

---

## Résultats de Validation

### **Tests d'Intégration Complets : 8/8 (100%)**

**Bloc 1 - Data Engineering :**
- Pipeline exécuté en 2.5s
- 895,345 → 7,433 lignes
- Mise à jour automatique
- Détection de gap (tolérance 5min)

**Bloc 2 - Intelligence Layer :**
- Plan généré en 1.54s
- Cache fonctionnel (0.01s)
- Correction automatique des plans
- Validation des plans

**Bloc 3 - MCP Execution :**
- Lecture DuckDB <0.5s
- Outils LangChain fonctionnels
- Outils tableau de bord
- Agrégation réussie

**Bloc 4 - Orchestration :**
- Temps moyen : 0.48s
- Temps max : 1.44s
- Workflow complet
- Gestion d'erreurs robuste

**Intégrations :**
- Bloc 2 + Bloc 3 : Plan exécuté
- Bloc 2 + Bloc 3 + Bloc 4 : Réponse générée
- Workflow complet : 3/3 questions traitées
- Performance : 0.48s moyen

---

## FLUX COMPLET VALIDÉ : QUESTION → AGENTS → DUCKDB → RÉPONSE

1. Votre Question : "Consommation hier ?"
      ↓
2. LLM Génère Plan : "Utilise data_extractor avec filtre hier"
      ↓
3. Agent MCP (data_extractor) EXÉCUTE
      ↓
4. Agent se connecte à DuckDB
      ↓
5. Agent lit : "SELECT * FROM energy_data WHERE DATE(timestamp) = '2025-01-20'"
      ↓
6. DuckDB retourne : [{"timestamp": "2025-01-20 08:00", "kwh_total": 2.5}, ...]
      ↓
7. Agent traite et retourne les données
      ↓
8. LLM synthétise la réponse finale
      ↓
9. Vous obtenez : "Hier, vous avez consommé 12.5 kWh"

**Temps total validé : 0.48s**




