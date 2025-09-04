#!/usr/bin/env python3
"""
📊 STANDARD RESPONSE CONTRACT
============================

Contrat de données uniforme pour tous les agents.
Élimine les problèmes de formats incohérents.
"""

from typing import Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import logging

class ResponseStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"

class ResponseType(Enum):
    CONSUMPTION = "consumption"
    COST = "cost"
    ZONES = "zones"
    MOYENNE = "moyenne"
    FORECAST = "forecast"

@dataclass
class StandardResponse:
    """Format uniforme pour toutes les réponses d'agents"""
    
    # Données principales
    value: float
    unit: str
    status: ResponseStatus
    response_type: ResponseType
    
    # Contexte
    question: str
    period: str
    aggregation: str
    
    # Métadonnées
    metadata: Dict[str, Any]
    
    # Réponse formatée
    answer: str
    
    # Source et traçabilité
    source: str
    agent_chain: list
    
    def __post_init__(self):
        """Validation après initialisation"""
        if self.value < 0:
            logging.warning(f"Valeur négative détectée: {self.value}")
        
        if not self.answer:
            self.answer = self._generate_default_answer()
    
    def _generate_default_answer(self) -> str:
        """Génère une réponse par défaut si manquante"""
        if self.response_type == ResponseType.MOYENNE:
            return f"📊 Votre consommation moyenne est de {self.value:.1f} {self.unit}."
        elif self.response_type == ResponseType.COST:
            return f"💰 Le coût est de {self.value:.2f} {self.unit}."
        elif self.response_type == ResponseType.ZONES:
            return f"🏠 Analyse des zones: {self.value:.1f} {self.unit}."
        else:
            return f"⚡ Résultat: {self.value:.1f} {self.unit}."
    
    def to_dict(self) -> Dict[str, Any]:
        """Conversion en dictionnaire pour compatibilité"""
        return {
            'question': self.question,
            'answer': self.answer,
            'value': self.value,
            'unit': self.unit,
            'period': self.period,
            'status': self.status.value,
            'type': self.response_type.value,
            'source': self.source,
            'metadata': self.metadata,
            'agent_chain': self.agent_chain
        }
    
    @classmethod
    def from_mcp_result(cls, question: str, mcp_result: Dict[str, Any], response_type: ResponseType) -> 'StandardResponse':
        """Crée une StandardResponse à partir d'un résultat MCP"""
        
        # Extraction intelligente de la valeur (résout le problème de formatage)
        value = cls._extract_value(mcp_result)
        
        # Extraction des métadonnées
        data = mcp_result.get('data', {})
        period = data.get('period', 'unknown')
        aggregation = data.get('aggregation', 'unknown')
        
        # Détermination de l'unité
        unit = cls._determine_unit(response_type, data)
        
        return cls(
            value=value,
            unit=unit,
            status=ResponseStatus.SUCCESS if mcp_result.get('status') == 'success' else ResponseStatus.ERROR,
            response_type=response_type,
            question=question,
            period=period,
            aggregation=aggregation,
            metadata=data,
            answer="",  # Sera généré automatiquement
            source=mcp_result.get('source', 'mcp'),
            agent_chain=['mcp']
        )
    
    @staticmethod
    def _extract_value(mcp_result: Dict[str, Any]) -> float:
        """🔧 Extraction intelligente de la valeur (corrige les erreurs DataFrame)"""
        data = mcp_result.get('data', {})
        
        # 🚨 PRIORITÉ: Vérifier les erreurs DataFrame
        if 'error' in data:
            error_msg = data['error']
            logging.error(f"Erreur MCP détectée: {error_msg}")
            # Ne pas retourner de valeur fallback hardcodée, laisser le workflow gérer l'erreur
            return 0.0
        
        # Format 1: data.value directe
        if 'value' in data:
            try:
                return float(data['value'])
            except (ValueError, TypeError):
                pass
        
        # Format 2: data.summary.total
        if 'summary' in data and 'total' in data['summary']:
            try:
                return float(data['summary']['total'])
            except (ValueError, TypeError):
                pass
        
        # Format 3: data.data.summary.total (format complexe)
        if 'data' in data and isinstance(data['data'], dict):
            nested_data = data['data']
            if 'summary' in nested_data and 'total' in nested_data['summary']:
                try:
                    return float(nested_data['summary']['total'])
                except (ValueError, TypeError):
                    pass
            if 'value' in nested_data:
                try:
                    return float(nested_data['value'])
                except (ValueError, TypeError):
                    pass
        
        # Format 4: Directement dans le résultat
        if 'value' in mcp_result:
            try:
                return float(mcp_result['value'])
            except (ValueError, TypeError):
                pass
        
        # Format 5: Zones (cas spécial)
        if 'zones' in data:
            zones = data['zones']
            if isinstance(zones, dict):
                try:
                    return sum(float(v) for v in zones.values() if isinstance(v, (int, float)))
                except (ValueError, TypeError):
                    pass
        
        # Format 6: Comparaisons temporelles
        if 'current_period' in data:
            try:
                return float(data['current_period'])
            except (ValueError, TypeError):
                pass
        
        # Fallback avec valeur réaliste
        logging.warning(f"Impossible d'extraire la valeur de: {mcp_result}")
        return 0.0
    
    @staticmethod
    def _determine_unit(response_type: ResponseType, data: Dict[str, Any]) -> str:
        """Détermine l'unité appropriée"""
        if response_type == ResponseType.COST:
            return "€"
        elif response_type == ResponseType.MOYENNE:
            granularity = data.get('granularity', 'day')
            if granularity == 'day':
                return "kWh/jour"
            elif granularity == 'week':
                return "kWh/semaine"
            else:
                return "kWh"
        else:
            return "kWh"

class ResponseBuilder:
    """Constructeur de réponses standardisées"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def _add_warmth_and_empathy(self, base_response: str, question: str) -> str:
        """🌟 Ajoute de l'empathie et de la chaleur à la réponse"""
        
        # 🎯 Phrases d'empathie et de chaleur
        warm_prefixes = [
            "🌟 Excellente question ! ",
            "💡 Très bonne question ! ",
            "🎯 Bonne question ! ",
            "✨ Intéressante question ! ",
            "👏 Belle question ! ",
            "💪 Question pertinente ! ",
            "🎉 Question intéressante ! ",
            "⭐ Question utile ! ",
            "🔥 Question importante ! ",
            "💎 Question bien formulée ! "
        ]
        
        # 🎯 Phrases de conclusion chaleureuses
        warm_suffixes = [
            " C'est une information très utile pour suivre votre consommation !",
            " Cela vous donne une bonne idée de vos habitudes énergétiques !",
            " C'est parfait pour optimiser votre consommation !",
            " Vous avez maintenant une vision claire de votre usage !",
            " C'est très utile pour votre suivi énergétique !",
            " Cela vous aide à mieux comprendre votre consommation !",
            " C'est excellent pour votre gestion énergétique !",
            " Vous avez maintenant toutes les informations nécessaires !",
            " C'est très utile pour votre optimisation énergétique !",
            " Cela vous donne une belle perspective de votre consommation !"
        ]
        
        # 🎯 Phrases d'encouragement pour les moyennes
        encouragement_suffixes = [
            " Continuez à surveiller vos habitudes !",
            " C'est un bon indicateur de votre consommation !",
            " Cela vous aide à optimiser votre usage !",
            " C'est parfait pour votre suivi quotidien !",
            " Vous avez une belle maîtrise de votre consommation !",
            " C'est excellent pour votre gestion énergétique !",
            " Cela vous donne une vision claire de vos habitudes !",
            " C'est très utile pour votre optimisation !",
            " Vous avez maintenant un bon repère !",
            " C'est parfait pour votre suivi énergétique !"
        ]
        
        import random
        
        # 🎯 Choisir un préfixe chaleureux
        prefix = random.choice(warm_prefixes)
        
        # 🎯 Choisir un suffixe selon le type de réponse
        question_lower = question.lower()
        if any(word in question_lower for word in ['moyenne', 'moyen', 'par jour', 'par heure', 'quotidien']):
            suffix = random.choice(encouragement_suffixes)
        else:
            suffix = random.choice(warm_suffixes)
        
        # 🎯 Construire la réponse chaleureuse
        warm_response = f"{prefix}{base_response}{suffix}"
        
        return warm_response
    
    def build_consumption_response(self, question: str, mcp_result: Dict[str, Any], semantic_validation: Dict[str, Any] = None) -> StandardResponse:
        """🔧 Construit une réponse de consommation intelligente (corrige l'incohérence temporelle)"""
        response = StandardResponse.from_mcp_result(question, mcp_result, ResponseType.CONSUMPTION)
        
        # 🆕 PRIORITÉ: Utiliser la validation sémantique si disponible
        if semantic_validation and semantic_validation.get('validated_period'):
            validated_period = semantic_validation['validated_period']
            period_mapping = {
                'current_month': 'ce mois-ci',
                'last_month': 'le mois dernier', 
                'current_year': 'cette année',
                'last_year': 'l\'année dernière',
                'current_week': 'cette semaine',
                '30d': 'ces 30 derniers jours',
                '7d': 'ces 7 derniers jours',
                '1d': 'hier',
                '1d_avant_hier': 'avant-hier'  # 🔧 CORRECTION : Ajouter avant-hier
            }
            period_text = period_mapping.get(validated_period, f'sur la période demandée')
        else:
            # Fallback: formatage intelligent basé sur la QUESTION
            question_lower = question.lower()
            
            # Détection intelligente de la période demandée dans la question
            if 'hier' in question_lower:
                period_text = 'hier'
            elif 'avant-hier' in question_lower or 'avant hier' in question_lower:
                period_text = 'avant-hier'  # 🔧 CORRECTION : Ajouter avant-hier
            elif 'ce mois' in question_lower or 'mois-ci' in question_lower:
                period_text = 'ce mois-ci'
            elif 'mois dernier' in question_lower or 'dernier mois' in question_lower:
                period_text = 'le mois dernier'
            elif 'cette semaine' in question_lower or 'semaine-ci' in question_lower:
                period_text = 'cette semaine'
            elif 'semaine dernière' in question_lower or 'dernière semaine' in question_lower:
                period_text = 'la semaine dernière'
            elif 'semaine passée' in question_lower or 'semaine écoulée' in question_lower:
                period_text = 'la semaine passée'
            elif 'semaine' in question_lower and 'dernière' in question_lower:
                period_text = 'la semaine dernière'  # 🔧 CORRECTION : Capturer "semaine dernière"
            elif 'consommation' in question_lower and 'semaine' in question_lower and 'dernière' in question_lower:
                period_text = 'la semaine dernière'  # 🔧 CORRECTION : Capturer "consommation semaine dernière"
            elif 'cette année' in question_lower or 'année-ci' in question_lower:
                period_text = 'cette année'
            elif 'par jour' in question_lower:
                period_text = 'par jour'
            elif 'par semaine' in question_lower:
                period_text = 'par semaine'
            elif 'par mois' in question_lower:
                period_text = 'par mois'
            elif 'par année' in question_lower or 'par an' in question_lower:
                period_text = 'par année'
            else:
                # Fallback sur le mapping technique si pas de correspondance
                period_text = {
                    '1d': 'hier',
                    '7d': 'cette semaine',
                    '30d': 'ces 30 derniers jours',
                    '365d': 'cette année'
                }.get(response.period, f'sur la période demandée')
        
        response.answer = f"⚡ Vous avez consommé {response.value:.1f} kWh {period_text}."
        # 🌟 Ajouter de l'empathie et de la chaleur
        response.answer = self._add_warmth_and_empathy(response.answer, question)
        return response
    
    def build_moyenne_response(self, question: str, mcp_result: Dict[str, Any]) -> StandardResponse:
        """Construit une réponse de moyenne intelligente"""
        response = StandardResponse.from_mcp_result(question, mcp_result, ResponseType.MOYENNE)
        
        # Formatage intelligent basé sur la question ET les métadonnées
        question_lower = question.lower()
        granularity = response.metadata.get('granularity', 'day')
        
        # 🔧 Détecter la période spécifique dans la question
        period_context = ""
        if 'mois dernier' in question_lower:
            period_context = " le mois dernier"
        elif 'semaine dernière' in question_lower:
            period_context = " la semaine dernière"
        elif 'année dernière' in question_lower:
            period_context = " l'année dernière"
        
        # PRIORITÉ: Détecter la granularité dans la question d'abord
        if 'par an' in question_lower or 'par année' in question_lower or 'annuelle' in question_lower:
            response.answer = f"📊 Votre consommation moyenne par an{period_context} est de {response.value:.0f} kWh/an."
        elif 'par mois' in question_lower or 'mensuelle' in question_lower:
            response.answer = f"📈 Votre consommation moyenne par mois{period_context} est de {response.value:.1f} kWh/mois."
        elif 'par semaine' in question_lower or 'hebdomadaire' in question_lower:
            response.answer = f"📊 Votre consommation moyenne par semaine{period_context} est de {response.value:.1f} kWh/semaine."
        elif 'par jour' in question_lower or 'quotidienne' in question_lower or 'journalière' in question_lower:
            response.answer = f"📅 Votre consommation moyenne par jour{period_context} est de {response.value:.1f} kWh/jour."
        elif 'par heure' in question_lower or 'horaire' in question_lower:
            response.answer = f"⏰ Votre consommation moyenne par heure{period_context} est de {response.value:.2f} kWh/h."
        # Fallback sur les métadonnées si pas trouvé dans la question
        elif granularity in ['année', 'year']:
            response.answer = f"📊 Votre consommation moyenne par an est de {response.value:.0f} kWh/an."
        elif granularity in ['mois', 'month']:
            response.answer = f"📈 Votre consommation moyenne par mois est de {response.value:.1f} kWh/mois."
        elif granularity in ['semaine', 'week']:
            response.answer = f"📊 Votre consommation moyenne par semaine est de {response.value:.1f} kWh/semaine."
        elif granularity in ['jour', 'day']:
            response.answer = f"📅 Votre consommation moyenne par jour est de {response.value:.1f} kWh/jour."
        elif granularity in ['heure', 'hour']:
            response.answer = f"⏰ Votre consommation moyenne par heure est de {response.value:.2f} kWh/h."
        else:
            response.answer = f"📊 Votre consommation moyenne est de {response.value:.1f} {response.unit}."
        
        # 🌟 Ajouter de l'empathie et de la chaleur
        response.answer = self._add_warmth_and_empathy(response.answer, question)
        return response
    
    def build_cost_response(self, question: str, mcp_result: Dict[str, Any]) -> StandardResponse:
        """Construit une réponse de coût"""
        response = StandardResponse.from_mcp_result(question, mcp_result, ResponseType.COST)
        
        data = response.metadata
        consumption = data.get('consumption_kwh', 0)
        advice = data.get('advice')
        
        if advice:
            response.answer = f"💡 {advice}. Coût actuel: {response.value:.2f}€ pour {consumption:.1f} kWh."
        else:
            response.answer = f"💰 Le coût est de {response.value:.2f}€ pour une consommation de {consumption:.1f} kWh."
        
        # 🌟 Ajouter de l'empathie et de la chaleur
        response.answer = self._add_warmth_and_empathy(response.answer, question)
        return response
    
    def build_zones_response(self, question: str, mcp_result: Dict[str, Any]) -> StandardResponse:
        """Construit une réponse de comparaison de zones"""
        response = StandardResponse.from_mcp_result(question, mcp_result, ResponseType.ZONES)
        
        data = response.metadata
        zones = data.get('zones', {})
        
        if zones:
            max_zone = max(zones.items(), key=lambda x: x[1])
            zone_name, zone_value = max_zone
            
            zone_names = {
                'cuisine': 'la cuisine',
                'buanderie': 'la buanderie', 
                'chauffage': 'le chauffage'
            }
            
            response.answer = f"🏠 {zone_names.get(zone_name, zone_name)} consomme le plus avec {zone_value:.1f} kWh. Total: {response.value:.1f} kWh."
        else:
            response.answer = "Aucune donnée de zones disponible."
        
        # 🌟 Ajouter de l'empathie et de la chaleur
        response.answer = self._add_warmth_and_empathy(response.answer, question)
        return response
    
    def build_temporal_response(self, question: str, mcp_result: Dict[str, Any], semantic_validation: Dict[str, Any] = None) -> StandardResponse:
        """🆕 Construit une réponse temporelle spécifique"""
        response = StandardResponse.from_mcp_result(question, mcp_result, ResponseType.CONSUMPTION)
        
        # 🆕 PRIORITÉ: Utiliser la validation sémantique pour le formatage
        if semantic_validation and semantic_validation.get('validated_period'):
            validated_period = semantic_validation['validated_period']
            
            if validated_period == 'current_month':
                response.answer = f"📅 Vous avez consommé {response.value:.1f} kWh ce mois-ci."
            elif validated_period == 'last_month':
                response.answer = f"📅 Vous avez consommé {response.value:.1f} kWh le mois dernier."
            elif validated_period == 'current_year':
                response.answer = f"📅 Vous avez consommé {response.value:.1f} kWh cette année."
            elif validated_period == 'last_year':
                response.answer = f"📅 Vous avez consommé {response.value:.1f} kWh l'année dernière."
            elif validated_period == '1d':
                response.answer = f"⚡ Vous avez consommé {response.value:.1f} kWh hier."
            elif validated_period == '1d_avant_hier':
                response.answer = f"⚡ Vous avez consommé {response.value:.1f} kWh avant-hier."
            elif validated_period == '7d' and ('semaine dernière' in question.lower() or 'dernière semaine' in question.lower()):
                response.answer = f"⚡ Vous avez consommé {response.value:.1f} kWh la semaine dernière."
            else:
                response.answer = f"⚡ Vous avez consommé {response.value:.1f} kWh sur la période demandée."
        else:
            # Fallback: formatage intelligent selon la question
            question_lower = question.lower()
            
            if 'hier' in question_lower:
                response.answer = f"⚡ Vous avez consommé {response.value:.1f} kWh hier."
            elif 'avant-hier' in question_lower or 'avant hier' in question_lower:
                response.answer = f"⚡ Vous avez consommé {response.value:.1f} kWh avant-hier."
            elif 'mois dernier' in question_lower:
                response.answer = f"📅 Vous avez consommé {response.value:.1f} kWh le mois dernier."
            elif 'mois' in question_lower:
                response.answer = f"📅 Vous avez consommé {response.value:.1f} kWh ce mois-ci."
            elif 'heure' in question_lower:
                response.answer = f"⏰ Votre consommation par heure est de {response.value/24:.2f} kWh en moyenne."
            elif 'augmenté' in question_lower:
                # Pour les questions d'évolution, on pourrait ajouter une logique de comparaison
                response.answer = f"📈 Votre consommation actuelle est de {response.value:.1f} kWh."
            elif 'weekend' in question_lower:
                response.answer = f"🏖️ Analyse weekend/semaine: {response.value:.1f} kWh total."
            else:
                response.answer = f"⚡ Vous avez consommé {response.value:.1f} kWh sur la période demandée."
        
        # 🌟 Ajouter de l'empathie et de la chaleur
        response.answer = self._add_warmth_and_empathy(response.answer, question)
        return response
    
    def build_granularity_response(self, question: str, mcp_result: Dict[str, Any], semantic_validation: Dict[str, Any] = None) -> StandardResponse:
        """🆕 Construit une réponse de granularité (par heure, par jour, etc.)"""
        response = StandardResponse.from_mcp_result(question, mcp_result, ResponseType.CONSUMPTION)
        
        # Extraire la granularité de la validation sémantique
        granularity = None
        if semantic_validation and semantic_validation.get('validated_period'):
            granularity = semantic_validation['validated_period']
        
        # Ou de l'exécution MCP
        if not granularity and mcp_result.get('data', {}).get('granularity'):
            granularity = mcp_result['data']['granularity']
        
        # Formatage selon la granularité
        granularity_formats = {
            'hourly': f"⏰ Votre consommation moyenne par heure est de {response.value:.2f} kWh/h.",
            'daily': f"📅 Votre consommation moyenne par jour est de {response.value:.1f} kWh/jour.",
            'weekly': f"📊 Votre consommation moyenne par semaine est de {response.value:.1f} kWh/semaine.",
            'monthly': f"📈 Votre consommation moyenne par mois est de {response.value:.1f} kWh/mois.",
            'yearly': f"📊 Votre consommation moyenne par an est de {response.value:.0f} kWh/an."
        }
        
        response.answer = granularity_formats.get(granularity, f"📊 Votre consommation moyenne est de {response.value:.2f} kWh par unité de temps.")
        
        # 🌟 Ajouter de l'empathie et de la chaleur
        response.answer = self._add_warmth_and_empathy(response.answer, question)
        return response
    
    def build_comparison_response(self, question: str, mcp_result: Dict[str, Any]) -> StandardResponse:
        """🆕 Construit une réponse de comparaison intelligente"""
        response = StandardResponse.from_mcp_result(question, mcp_result, ResponseType.CONSUMPTION)
        
        # Formatage intelligent selon le type de comparaison
        question_lower = question.lower()
        
        if 'été' in question_lower and 'hiver' in question_lower:
            response.answer = f"🌞❄️ Comparaison saisonnière: Les données montrent une consommation de {response.value:.1f} kWh. Une analyse plus détaillée nécessiterait des données saisonnières spécifiques."
        elif 'dernier' in question_lower or 'précédent' in question_lower:
            response.answer = f"📈 Comparaison temporelle: Votre consommation actuelle est de {response.value:.1f} kWh. L'évolution par rapport à la période précédente nécessite une analyse comparative."
        elif 'weekend' in question_lower and 'semaine' in question_lower:
            response.answer = f"🏖️ Comparaison weekend/semaine: Analyse des habitudes de consommation - {response.value:.1f} kWh total observé."
        elif 'année' in question_lower or 'annuel' in question_lower:
            response.answer = f"📅 Consommation annuelle: {response.value:.1f} kWh sur la période analysée."
        else:
            response.answer = f"📊 Analyse comparative: {response.value:.1f} kWh observé pour la comparaison demandée."
        
        # 🌟 Ajouter de l'empathie et de la chaleur
        response.answer = self._add_warmth_and_empathy(response.answer, question)
        return response
