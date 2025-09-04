#!/usr/bin/env python3
"""
🔄 Script de préparation du projet Energy-Agent pour GitHub
================================================================

Ce script prépare le projet pour le partage sur GitHub en :
- Excluant les fichiers inutiles (cache, données sensibles, etc.)
- Créant une structure optimisée
- Générant un fichier .gitignore approprié
- Créant un script d'installation automatique
"""

import os
import shutil
import zipfile
from pathlib import Path
import json

class GitHubPreparator:
    """Préparateur de projet pour GitHub"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.output_dir = self.project_root / "github_ready"
        self.excluded_patterns = [
            # Fichiers système
            ".DS_Store",
            "Thumbs.db",
            "*.swp",
            "*.swo",
            
            # Cache Python
            "__pycache__/",
            "*.pyc",
            "*.pyo",
            "*.pyd",
            ".pytest_cache/",
            ".mypy_cache/",
            
            # Environnements virtuels
            ".venv/",
            "venv/",
            "env/",
            
            # IDE
            ".vscode/",
            ".idea/",
            "*.sublime-*",
            
            # Données sensibles et volumineuses
            "*.duckdb",
            "*.db",
            ".env",
            "*.log",
            
            # Fichiers temporaires
            "*.tmp",
            "*.temp",
            "*.bak",
            
            # Build et distribution
            "build/",
            "dist/",
            "*.egg-info/",
            
            # Données de développement
            "data_genere/processed/*.duckdb",
            "data_genere/backups/",
            "data_genere/raw/",
            
            # Fichiers de test temporaires
            "test_*.py",
            "debug_*.py",
            
            # Fichiers obsolètes
            "app_old.py",
            "app copy.py",
            "app2 copy.py",
        ]
        
        self.included_directories = [
            "orchestration/",
            "mcp_server/",
            "core/",
            "data_genere_gap/",
            "llm_planner/",
            "docs/",
        ]
        
        self.essential_files = [
            "app2.py",
            "environment.yml",
            "README.md",
            "LICENSE",
            ".gitignore",
        ]
    
    def clean_directory(self, directory):
        """Nettoie un répertoire en supprimant les fichiers exclus"""
        for pattern in self.excluded_patterns:
            if pattern.endswith('/'):
                # Répertoire
                dir_pattern = directory / pattern.rstrip('/')
                if dir_pattern.exists():
                    print(f"🗑️  Suppression du répertoire: {dir_pattern}")
                    shutil.rmtree(dir_pattern, ignore_errors=True)
            else:
                # Fichier
                for file_path in directory.rglob(pattern):
                    if file_path.is_file():
                        print(f"🗑️  Suppression du fichier: {file_path}")
                        file_path.unlink()
    
    def copy_essential_files(self):
        """Copie les fichiers essentiels"""
        print("📁 Copie des fichiers essentiels...")
        
        for file_name in self.essential_files:
            source = self.project_root / file_name
            if source.exists():
                dest = self.output_dir / file_name
                shutil.copy2(source, dest)
                print(f"✅ Copié: {file_name}")
            else:
                print(f"⚠️  Fichier non trouvé: {file_name}")
    
    def copy_directories(self):
        """Copie les répertoires inclus"""
        print("📁 Copie des répertoires...")
        
        for dir_name in self.included_directories:
            source = self.project_root / dir_name
            if source.exists():
                dest = self.output_dir / dir_name
                shutil.copytree(source, dest, dirs_exist_ok=True)
                print(f"✅ Copié: {dir_name}")
                
                # Nettoyer le répertoire copié
                self.clean_directory(dest)
            else:
                print(f"⚠️  Répertoire non trouvé: {dir_name}")
    
    def create_sample_data(self):
        """Crée un échantillon de données pour la démonstration"""
        print("📊 Création d'échantillon de données...")
        
        sample_data_dir = self.output_dir / "data_genere" / "processed"
        sample_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Créer un fichier README pour les données
        data_readme = sample_data_dir / "README.md"
        data_readme.write_text("""
# 📊 Données Énergétiques

Ce répertoire contient les données de consommation électrique.

## 🚀 Première Utilisation

1. **Génération automatique** : L'application générera automatiquement les données au premier lancement
2. **Données fictives** : Les données sont générées de manière réaliste pour la démonstration
3. **Base DuckDB** : Format optimisé pour les requêtes analytiques

## 📋 Structure des Données

- **Période** : 2 ans de données fictives
- **Granularité** : Mesures toutes les 2 heures
- **Équipements** : Cuisine, Buanderie, Ballon d'eau chaude
- **Métriques** : Puissance, tension, consommation totale

## 🔧 Génération

```bash
# L'application génère automatiquement les données au premier lancement
streamlit run app2.py
```
""")
        
        print("✅ Échantillon de données créé")
    
    def create_installation_script(self):
        """Crée un script d'installation automatique"""
        print("🔧 Création du script d'installation...")
        
        install_script = self.output_dir / "install.sh"
        install_script.write_text("""#!/bin/bash
# 🚀 Script d'installation Energy-Agent
# ======================================

echo "⚡ Installation d'Energy Agent..."

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

# Vérifier Conda
if ! command -v conda &> /dev/null; then
    echo "❌ Conda n'est pas installé"
    echo "📥 Installez Conda depuis: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

# Créer l'environnement
echo "🔧 Création de l'environnement conda..."
conda env create -f environment.yml

# Activer l'environnement
echo "✅ Environnement créé avec succès!"
echo ""
echo "🚀 Pour lancer l'application:"
echo "   conda activate energy-agent"
echo "   streamlit run app2.py"
echo ""
echo "📖 Consultez le README.md pour plus d'informations"
""")
        
        # Rendre le script exécutable
        install_script.chmod(0o755)
        print("✅ Script d'installation créé")
    
    def create_windows_install_script(self):
        """Crée un script d'installation pour Windows"""
        print("🔧 Création du script d'installation Windows...")
        
        install_script = self.output_dir / "install.bat"
        install_script.write_text("""@echo off
REM 🚀 Script d'installation Energy-Agent (Windows)
REM ================================================

echo ⚡ Installation d'Energy Agent...

REM Vérifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé
    echo 📥 Installez Python depuis: https://python.org
    pause
    exit /b 1
)

REM Vérifier Conda
conda --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Conda n'est pas installé
    echo 📥 Installez Conda depuis: https://docs.conda.io/en/latest/miniconda.html
    pause
    exit /b 1
)

REM Créer l'environnement
echo 🔧 Création de l'environnement conda...
conda env create -f environment.yml

REM Activer l'environnement
echo ✅ Environnement créé avec succès!
echo.
echo 🚀 Pour lancer l'application:
echo    conda activate energy-agent
echo    streamlit run app2.py
echo.
echo 📖 Consultez le README.md pour plus d'informations
pause
""")
        
        print("✅ Script d'installation Windows créé")
    
    def create_github_gitignore(self):
        """Crée un .gitignore optimisé pour GitHub"""
        print("📝 Création du .gitignore GitHub...")
        
        gitignore_content = """# Energy Agent - .gitignore pour GitHub
# ================================================

# Variables d'environnement
.env
.env.local
.env.*.local

# Données sensibles et volumineuses
*.duckdb
*.db
*.sqlite
*.sqlite3

# Cache Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environnements virtuels
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
logs/

# Tests
.pytest_cache/
.coverage
htmlcov/

# Données de développement
data_genere/processed/*.duckdb
data_genere/backups/
data_genere/raw/

# Fichiers temporaires
*.tmp
*.temp
*.bak

# Fichiers de test temporaires
test_*.py
debug_*.py

# Fichiers obsolètes
app_old.py
app copy.py
app2 copy.py
"""
        
        gitignore_file = self.output_dir / ".gitignore"
        gitignore_file.write_text(gitignore_content)
        print("✅ .gitignore GitHub créé")
    
    def create_project_info(self):
        """Crée un fichier d'informations sur le projet"""
        print("📋 Création des informations projet...")
        
        project_info = {
            "name": "Energy Agent",
            "description": "Assistant Intelligent pour l'Analyse de Consommation Électrique",
            "version": "1.0.0",
            "author": "Votre Nom",
            "technologies": [
                "Python 3.11",
                "Streamlit",
                "LangGraph",
                "DuckDB",
                "Prophet",
                "Google Gemini"
            ],
            "features": [
                "Chat intelligent avec IA",
                "Tableau de bord interactif",
                "Prévisions Prophet",
                "Architecture agentique",
                "Interface moderne"
            ],
            "demo_video": "https://www.loom.com/share/bc94951d58f64ae1af4da87dba532ce6"
        }
        
        info_file = self.output_dir / "project_info.json"
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(project_info, f, indent=2, ensure_ascii=False)
        
        print("✅ Informations projet créées")
    
    def create_zip_archive(self):
        """Crée une archive ZIP du projet optimisé"""
        print("📦 Création de l'archive ZIP...")
        
        zip_path = self.project_root / "Energy-Agent-GitHub-Ready.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.output_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(self.output_dir)
                    zipf.write(file_path, arcname)
        
        print(f"✅ Archive créée: {zip_path}")
        print(f"📊 Taille: {zip_path.stat().st_size / (1024*1024):.1f} MB")
    
    def prepare_project(self):
        """Prépare le projet complet pour GitHub"""
        print("🚀 Préparation du projet Energy-Agent pour GitHub")
        print("=" * 60)
        
        # Nettoyer le répertoire de sortie
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
        self.output_dir.mkdir()
        
        # Étapes de préparation
        self.copy_essential_files()
        self.copy_directories()
        self.create_sample_data()
        self.create_installation_script()
        self.create_windows_install_script()
        self.create_github_gitignore()
        self.create_project_info()
        
        # Créer l'archive ZIP
        self.create_zip_archive()
        
        print("\n🎉 Projet préparé avec succès pour GitHub!")
        print("📁 Fichiers créés:")
        print(f"   📦 Archive: Energy-Agent-GitHub-Ready.zip")
        print(f"   📁 Dossier: {self.output_dir}")
        print("\n📋 Prochaines étapes:")
        print("   1. Décompressez l'archive sur GitHub")
        print("   2. Vérifiez que tous les fichiers sont présents")
        print("   3. Testez l'installation avec install.sh/install.bat")
        print("   4. Lancez l'application avec streamlit run app2.py")

def main():
    """Fonction principale"""
    preparator = GitHubPreparator()
    preparator.prepare_project()

if __name__ == "__main__":
    main()
