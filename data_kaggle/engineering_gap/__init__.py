"""
Module Data Engineering - Bloc 1
Gestion automatique des données et mise à jour
"""

from .data_checker import DataChecker
from .data_generator import DataGenerator
from .pipeline_runner import PipelineRunner
from .auto_update import AutoDataUpdater

__all__ = [
    'DataChecker',
    'DataGenerator', 
    'PipelineRunner',
    'AutoDataUpdater'
]

__version__ = "1.0.0"
__author__ = "Energy Agent Team"




