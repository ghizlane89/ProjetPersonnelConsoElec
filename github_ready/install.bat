@echo off
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
