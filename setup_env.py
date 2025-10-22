#!/usr/bin/env python3
"""
Configuration script for Energy Agent
Sets up environment variables and checks system status
"""

import os
import sys

def setup_environment():
    """Configure environment variables for Energy Agent"""
    
    print("🔧 Configuration de l'environnement Energy Agent")
    print("=" * 50)
    
    # Check if GEMINI_API_KEY is set
    gemini_key = os.getenv('GEMINI_API_KEY')
    if not gemini_key:
        print("⚠️  GEMINI_API_KEY non configurée")
        print("📝 Pour configurer votre clé API Gemini :")
        print("   1. Obtenez une clé API sur https://makersuite.google.com/app/apikey")
        print("   2. Exécutez : export GEMINI_API_KEY='votre_clé_api'")
        print("   3. Ou ajoutez-la à votre fichier ~/.bashrc ou ~/.zshrc")
        print()
        return False
    else:
        print(f"✅ GEMINI_API_KEY configurée (début: {gemini_key[:10]}...)")
    
    # Check database
    db_path = "data_genere/processed/energy_fictional_2h.duckdb"
    if os.path.exists(db_path):
        print(f"✅ Base de données trouvée : {db_path}")
        try:
            import duckdb
            conn = duckdb.connect(db_path)
            count = conn.execute("SELECT COUNT(*) FROM energy_data").fetchone()[0]
            print(f"📊 Données disponibles : {count:,} lignes")
            conn.close()
        except Exception as e:
            print(f"❌ Erreur base de données : {e}")
            return False
    else:
        print(f"❌ Base de données manquante : {db_path}")
        return False
    
    print()
    print("🎉 Configuration terminée avec succès !")
    return True

def show_usage():
    """Show usage instructions"""
    print()
    print("🚀 UTILISATION")
    print("=" * 30)
    print("1. Configurez GEMINI_API_KEY :")
    print("   export GEMINI_API_KEY='votre_clé_api_gemini'")
    print()
    print("2. Lancez l'application :")
    print("   streamlit run app2.py")
    print()
    print("3. Accédez à l'interface :")
    print("   http://localhost:8501")

if __name__ == "__main__":
    success = setup_environment()
    show_usage()
    
    if not success:
        sys.exit(1)

