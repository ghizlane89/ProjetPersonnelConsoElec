#!/usr/bin/env python3
"""
🔧 MCP SERVER - BLOC 3
======================

Serveur MCP pour exécution des plans JSON générés par le BLOC 2.
Outils génériques basés sur LangChain et Plotly.

Critères d'acceptation :
- Endpoints sécurisés
- Validation des arguments
- Lecture/écriture DuckDB OK
- Retour JSON propre
"""

from .core.mcp_server import get_mcp_server, MCPServer
from .core.energy_mcp_tools import get_energy_tools, EnergyMCPTools
from .core.dashboard_tools import get_dashboard_tools, DashboardTools
from .core.database_manager import get_database_manager, DatabaseManager

__version__ = "1.0.0"
__author__ = "Energy Agent Team"

# Exports principaux
__all__ = [
    'get_mcp_server',
    'MCPServer',
    'get_energy_tools',
    'EnergyMCPTools',
    'get_dashboard_tools',
    'DashboardTools',
    'get_database_manager',
    'DatabaseManager'
]





