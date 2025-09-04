"""
🔧 Data Générée - Gestion des Gaps
=================================

Module pour la gestion automatique des données manquantes.

Composants :
- GapDetector : Détection des gaps temporels
- GapGenerator : Génération de données de continuité  
- GapUpdater : Mise à jour DuckDB
- GapManager : Orchestration complète
"""

from .gap_detector import GapDetector
from .gap_generator import GapGenerator  
from .gap_updater import GapUpdater
from .gap_manager import GapManager

__all__ = [
    'GapDetector',
    'GapGenerator', 
    'GapUpdater',
    'GapManager'
]








