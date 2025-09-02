#!/usr/bin/env python3
"""
🔒 GESTIONNAIRE DUCKDDB SÉCURISÉ - BLOC 3
=========================================

Gestionnaire sécurisé pour les connexions DuckDB.
Validation des requêtes et gestion des erreurs.

Critères d'acceptation :
- Lecture/écriture DuckDB OK
- Endpoints sécurisés
- Validation des arguments
"""

import os
import duckdb
import pandas as pd
from typing import Dict, Any, Optional, List
from contextlib import contextmanager
import logging

class DatabaseManager:
    """Gestionnaire sécurisé pour DuckDB"""
    
    def __init__(self, db_path: str):
        """Initialisation du gestionnaire de base de données"""
        self.db_path = db_path
        self.connection = None
        self.logger = logging.getLogger(__name__)
        
        # Validation du chemin
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Base de données non trouvée: {db_path}")
        
        # Connexion sécurisée
        self._connect()
        self._validate_connection()
        
        print(f"✅ Gestionnaire DuckDB initialisé: {db_path}")
    
    def _connect(self):
        """Établir une connexion sécurisée"""
        try:
            self.connection = duckdb.connect(self.db_path, read_only=False)
            # Configuration de sécurité
            self.connection.execute("SET enable_progress_bar=false")
            self.connection.execute("SET memory_limit='1GB'")
        except Exception as e:
            raise ConnectionError(f"Erreur de connexion DuckDB: {e}")
    
    def _validate_connection(self):
        """Valider la connexion et la structure"""
        try:
            # Vérifier que la table existe
            tables = self.connection.execute("SHOW TABLES").fetchall()
            if not tables:
                raise ValueError("Aucune table trouvée dans la base de données")
            
            # Vérifier la structure de la table principale
            schema = self.connection.execute("DESCRIBE energy_data").fetchall()
            required_columns = ['timestamp', 'global_active_power_kw', 'voltage_v', 'global_intensity_a']
            
            existing_columns = [col[0] for col in schema]
            missing_columns = [col for col in required_columns if col not in existing_columns]
            
            if missing_columns:
                raise ValueError(f"Colonnes manquantes: {missing_columns}")
                
        except Exception as e:
            raise ValueError(f"Validation de la base de données échouée: {e}")
    
    @contextmanager
    def get_connection(self):
        """Contexte manager pour les connexions sécurisées"""
        try:
            yield self.connection
        except Exception as e:
            self.logger.error(f"Erreur de base de données: {e}")
            raise
        finally:
            # Pas de fermeture automatique pour maintenir la connexion
            pass
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> pd.DataFrame:
        """
        Exécuter une requête sécurisée
        
        Args:
            query: Requête SQL
            params: Paramètres de la requête
            
        Returns:
            DataFrame avec les résultats
        """
        try:
            # Validation de la requête
            self._validate_query(query)
            
            with self.get_connection() as conn:
                if params:
                    result = conn.execute(query, params).fetchdf()
                else:
                    result = conn.execute(query).fetchdf()
                
                return result
                
        except Exception as e:
            self.logger.error(f"Erreur d'exécution de requête: {e}")
            raise
    
    def _validate_query(self, query: str):
        """Valider la sécurité de la requête"""
        # Protection contre les injections SQL basiques
        dangerous_keywords = [
            'DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'INSERT', 'UPDATE',
            'EXEC', 'EXECUTE', 'SCRIPT', 'BATCH', 'COMMAND'
        ]
        
        query_upper = query.upper()
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                raise ValueError(f"Opération non autorisée: {keyword}")
        
        # Protection contre les injections SQL avancées
        suspicious_patterns = [
            ';', '--', '/*', '*/', 'UNION', 'OR 1=1', 'OR TRUE'
        ]
        
        for pattern in suspicious_patterns:
            if pattern.upper() in query_upper:
                raise ValueError(f"Pattern suspect détecté: {pattern}")
        
        # Validation de la structure de base
        if not query.strip().upper().startswith('SELECT'):
            raise ValueError("Seules les requêtes SELECT sont autorisées")
    
    def get_table_info(self, table_name: str = "energy_data") -> Dict[str, Any]:
        """Obtenir les informations sur une table"""
        try:
            with self.get_connection() as conn:
                # Informations de base
                schema = conn.execute(f"DESCRIBE {table_name}").fetchall()
                
                # Statistiques
                row_count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
                
                # Période de données
                date_range = conn.execute(f"""
                    SELECT 
                        MIN(timestamp) as min_date,
                        MAX(timestamp) as max_date
                    FROM {table_name}
                """).fetchone()
                
                return {
                    "table_name": table_name,
                    "schema": [{"column": col[0], "type": col[1]} for col in schema],
                    "row_count": row_count,
                    "date_range": {
                        "min_date": str(date_range[0]),
                        "max_date": str(date_range[1])
                    }
                }
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des infos table: {e}")
            raise
    
    def get_sample_data(self, table_name: str = "energy_data", limit: int = 10) -> pd.DataFrame:
        """Obtenir un échantillon de données"""
        try:
            query = f"SELECT * FROM {table_name} ORDER BY timestamp DESC LIMIT {limit}"
            return self.execute_query(query)
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération d'échantillon: {e}")
            raise
    
    def close(self):
        """Fermer la connexion"""
        if self.connection:
            self.connection.close()
            print("🔒 Connexion DuckDB fermée")

# Instance globale
_database_manager: Optional[DatabaseManager] = None

def get_database_manager() -> DatabaseManager:
    """Retourne l'instance globale du gestionnaire de base de données"""
    global _database_manager
    if _database_manager is None:
        # Gérer les chemins relatifs depuis différents répertoires
        base_path = os.getenv('DUCKDB_PATH', 'data/processed/energy_2h_aggregated.duckdb')
        if not os.path.exists(base_path):
            # Essayer depuis le répertoire parent
            parent_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data/processed/energy_2h_aggregated.duckdb')
            if os.path.exists(parent_path):
                db_path = parent_path
            else:
                db_path = base_path
        else:
            db_path = base_path
        _database_manager = DatabaseManager(db_path)
    return _database_manager
