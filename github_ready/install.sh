#!/bin/bash
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
