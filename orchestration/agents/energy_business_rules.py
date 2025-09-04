#!/usr/bin/env python3
"""
🧠 ENERGY BUSINESS RULES AGENT
==============================

Agent spécialisé dans la logique métier énergétique.
Externalise toute la logique if/else de l'orchestrateur.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

@dataclass
class QuestionIntent:
    """Structure pour représenter l'intention d'une question"""
    intent_type: str  # 'moyenne', 'total', 'comparaison', 'coût'
    temporal: str     # 'jour', 'semaine', 'mois', 'hier'
    aggregation: str  # 'sum', 'mean', 'max', 'min'
    entities: list    # ['consommation', 'prix', 'zone']
    confidence: float # 0.0 à 1.0

@dataclass
class ExecutionStrategy:
    """Stratégie d'exécution basée sur l'intention"""
    tool_name: str
    parameters: Dict[str, Any]
    expected_format: str
    response_template: str

class EnergyBusinessRules:
    """Agent de règles métier pour l'énergie"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Mots-clés pour la détection d'intention
        self.intent_keywords = {
            'moyenne': ['moyenne', 'average', 'moyen', 'en moyenne'],
            'total': [
                # Questions de consommation simples (PRIORITÉ)
                'total', 'somme', 'consommé', 'consommation', 
                'combien', 'quelle', 'quel est',
                # Périodes simples
                'par semaine', 'par mois', 'par jour',
                'weekend', 'mois dernier', 'le mois dernier',
                'ces 7 derniers jours', 'ces 30 derniers jours',
                'cette semaine', 'ce mois-ci', 'samedi', 'dimanche'
            ],
            'comparaison': [
                # Comparaisons explicites SEULEMENT
                'été vs hiver', 'plus élevée que', 'plus faible que',
                'par rapport à', 'compare', 'versus', 'vs', 
                'différence entre', 'comparaison',
                # Évolutions explicites
                'a augmenté', 'a diminué', 'évolution', 'tendance'
            ],
            'temporal_specific': ['hier', 'yesterday', 'avant-hier', 'avant hier', 'semaine dernière', 'dernière semaine', 'mois-ci', 'ce mois', 'heure', 'par heure', 'par année', 'annuel'],
            'coût': ['coût', 'euro', '€', 'prix', 'économiser', 'argent'],
            'prévision': ['prévision', 'prévoir', 'futur', 'demain']
        }
        
        # 🆕 Questions simples qui ne sont PAS des comparaisons
        self.simple_questions = [
            'quelle est ma consommation',
            'consommation par',
            'ma consommation du',
            'combien ai-je consommé'
        ]
        
        self.temporal_keywords = {
            'hier': ['hier', 'yesterday'],
            'jour': ['jour', 'day', 'quotidien', 'journalier'],
            'semaine': ['semaine', 'week', 'hebdomadaire'],
            'mois': ['mois', 'month', 'mensuel'],
            'année': ['année', 'year', 'annuel']
        }
        
        self.aggregation_keywords = {
            'mean': ['moyenne', 'average', 'moyen'],
            'sum': ['total', 'somme', 'consommé'],
            'max': ['maximum', 'max', 'pic', 'pointe'],
            'min': ['minimum', 'min', 'plus faible']
        }
    
    def analyze_question_intent(self, question: str, validated_period: str = None) -> QuestionIntent:
        """Analyse l'intention d'une question"""
        question_lower = question.lower()
        
        # 🆕 Utiliser la période validée pour améliorer la détection d'intention
        if validated_period:
            # Si on a une période validée, adapter l'intent type
            if validated_period in ['current_month', 'last_month', 'current_year', 'last_year']:
                # Périodes calendaires → temporal_specific
                intent_type = 'temporal_specific'
            elif validated_period in ['30d', '7d', '1d']:
                # Périodes glissantes → peut rester total ou temporal_specific
                intent_type = self._detect_intent_type(question_lower)
                # Si c'est une question simple, forcer temporal_specific
                if intent_type == 'total' and any(word in question_lower for word in ['hier', 'mois', 'semaine']):
                    intent_type = 'temporal_specific'
            else:
                intent_type = self._detect_intent_type(question_lower)
        else:
            # Détecter le type d'intention normalement
            intent_type = self._detect_intent_type(question_lower)
        
        # Détecter l'aspect temporel (amélioré avec validation)
        temporal = self._detect_temporal(question_lower, validated_period)
        aggregation = self._detect_aggregation(question_lower, intent_type)
        entities = self._detect_entities(question_lower)
        confidence = self._calculate_confidence(question_lower, intent_type)
        
        return QuestionIntent(
            intent_type=intent_type,
            temporal=temporal,
            aggregation=aggregation,
            entities=entities,
            confidence=confidence
        )
    
    def _detect_intent_type(self, question: str) -> str:
        """🔧 Détecte le type d'intention principal (corrige la sur-classification)"""
        question_lower = question.lower()
        
        # 🚨 PRIORITÉ 1: Vérifier si c'est une question simple
        for simple_pattern in self.simple_questions:
            if simple_pattern in question_lower:
                # Question simple détectée, vérifier le type spécifique
                if 'moyenne' in question_lower:
                    return 'moyenne'
                elif any(temp in question_lower for temp in ['hier', 'par heure', 'par année']):
                    return 'temporal_specific'
                else:
                    return 'total'  # Question simple de consommation
        
        # 🚨 PRIORITÉ 1.5: Vérifier les périodes spécifiques
        if any(temp in question_lower for temp in ['semaine dernière', 'dernière semaine', 'avant-hier', 'avant hier']):
            return 'temporal_specific'
        
        # 🚨 PRIORITÉ 2: Vérifier les comparaisons explicites (questions complexes)
        comparison_indicators = ['est-elle', 'plus élevée', 'plus faible', 'différente', 'compare', 'versus']
        has_comparison = any(indicator in question_lower for indicator in comparison_indicators)
        
        if has_comparison:
            # C'est vraiment une comparaison
            return 'comparaison'
        
        # PRIORITÉ 3: Logique normale
        for intent, keywords in self.intent_keywords.items():
            if any(keyword in question_lower for keyword in keywords):
                return intent
        return 'total'  # Par défaut
    
    def _detect_temporal(self, question: str, validated_period: str = None) -> str:
        """Détecte l'aspect temporel (amélioré avec validation sémantique)"""
        
        # 🆕 PRIORITÉ: Utiliser la période validée si disponible
        if validated_period:
            period_to_temporal = {
                'current_month': 'mois',
                'last_month': 'mois',
                'current_year': 'année',
                'last_year': 'année',
                'current_week': 'semaine',
                '30d': 'mois',
                '7d': 'semaine',
                '1d': 'jour'
            }
            return period_to_temporal.get(validated_period, 'semaine')
        
        # Sinon, logique normale
        for temporal, keywords in self.temporal_keywords.items():
            if any(keyword in question for keyword in keywords):
                return temporal
        return 'semaine'  # Par défaut
    
    def _detect_aggregation(self, question: str, intent_type: str) -> str:
        """Détecte le type d'agrégation"""
        # Si c'est une question de moyenne, forcer 'mean'
        if intent_type == 'moyenne':
            return 'mean'
        
        for agg, keywords in self.aggregation_keywords.items():
            if any(keyword in question for keyword in keywords):
                return agg
        return 'sum'  # Par défaut
    
    def _detect_entities(self, question: str) -> list:
        """Détecte les entités mentionnées"""
        entities = []
        if any(word in question for word in ['consommation', 'énergie', 'électricité']):
            entities.append('consommation')
        if any(word in question for word in ['prix', 'coût', 'euro', '€']):
            entities.append('prix')
        if any(word in question for word in ['zone', 'compteur', 'cuisine', 'chauffage']):
            entities.append('zone')
        return entities
    
    def _calculate_confidence(self, question: str, intent_type: str) -> float:
        """Calcule la confiance dans l'analyse"""
        # Simple heuristique basée sur le nombre de mots-clés trouvés
        keywords = self.intent_keywords.get(intent_type, [])
        matches = sum(1 for keyword in keywords if keyword in question)
        return min(matches * 0.3 + 0.4, 1.0)
    
    def get_execution_strategy(self, intent: QuestionIntent, llm_plan: Dict[str, Any], question: str = "", validated_period: str = None) -> ExecutionStrategy:
        """Détermine la stratégie d'exécution basée sur l'intention (corrigée par validation sémantique)"""
        
        # 🆕 CORRECTION: Utiliser la validation sémantique pour corriger l'intent type
        corrected_intent_type = intent.intent_type
        if validated_period:
            # PRIORITÉ: Si c'est déjà une question de moyenne, garder 'moyenne'
            if intent.intent_type == 'moyenne':
                corrected_intent_type = 'moyenne'  # Garder l'intention moyenne
            # Granularités → nouveau type d'intention (sauf si déjà moyenne)
            elif validated_period in ['hourly', 'daily', 'weekly', 'monthly', 'yearly']:
                corrected_intent_type = 'granularity'
            # Jours nommés → temporal_specific
            elif validated_period in ['saturday', 'sunday', 'weekend']:
                corrected_intent_type = 'temporal_specific'
            # Périodes calendaires mais classées comme comparaison, corriger
            elif validated_period in ['current_month', 'last_month', 'current_year', 'last_year']:
                if intent.intent_type == 'comparaison' and not any(word in question.lower() for word in ['plus élevée', 'différente', 'versus']):
                    corrected_intent_type = 'temporal_specific'
                # self.logger.info(f"🔧 Correction intent: {intent.intent_type} → {corrected_intent_type} (validation: {validated_period})")  # Logger pas toujours disponible
        
        # Stratégies spécialisées selon l'intention (corrigée)
        if corrected_intent_type == 'moyenne':
            return self._get_moyenne_strategy(intent, llm_plan, validated_period, question)
        elif corrected_intent_type == 'granularity':  # 🆕 Nouveau pour les granularités
            return self._get_granularity_strategy(intent, llm_plan, question, validated_period)
        elif corrected_intent_type == 'temporal_specific':  # 🆕 Nouveau
            return self._get_temporal_strategy(intent, llm_plan, question, validated_period)
        elif corrected_intent_type == 'comparaison':
            return self._get_comparaison_strategy(intent, llm_plan)
        elif corrected_intent_type == 'coût':
            return self._get_cout_strategy(intent, llm_plan)
        else:
            return self._get_default_strategy(intent, llm_plan, validated_period)
    
    def _get_moyenne_strategy(self, intent: QuestionIntent, llm_plan: Dict, validated_period: str = None, question: str = "") -> ExecutionStrategy:
        """Stratégie pour les questions de moyenne avec validation sémantique"""
        
        # Utiliser la période validée si disponible, sinon logique existante
        if validated_period:
            # 🔧 CORRECTION : Utiliser directement la période validée
            if validated_period in ['7d', '30d', '84d', '365d', '1825d']:
                period = validated_period
                # Déterminer la granularité selon la question
                if 'horaire' in question.lower() or 'heure' in question.lower():
                    granularity = 'heure'
                elif 'jour' in question.lower():
                    granularity = 'jour'
                elif 'semaine' in question.lower():
                    granularity = 'semaine'
                elif 'mois' in question.lower():
                    granularity = 'mois'
                elif 'an' in question.lower():
                    granularity = 'année'
                else:
                    granularity = 'jour'  # Par défaut
            else:
                # Mapper les granularités validées vers les paramètres appropriés
                granularity_mapping = {
                    'hourly': ('7d', 'heure'),
                    'daily': ('30d', 'jour'), 
                    'weekly': ('84d', 'semaine'),  # 12 semaines = 84 jours
                    'monthly': ('365d', 'mois'),   # 12 mois = 365 jours  
                    'yearly': ('1825d', 'année')   # 5 ans = 1825 jours
                }
                period, granularity = granularity_mapping.get(validated_period, ('30d', 'jour'))
        else:
            # Logique existante
            period = '7d' if intent.temporal in ['jour', 'hier'] else '30d'
            granularity = intent.temporal
        
        return ExecutionStrategy(
            tool_name='aggregate_moyenne',
            parameters={
                'aggregation': 'mean',
                'period': period,
                'granularity': granularity,
                'metric': 'consumption'
            },
            expected_format='moyenne',
            response_template='moyenne_response'
        )
    
    def _get_granularity_strategy(self, intent: QuestionIntent, llm_plan: Dict, question: str = "", validated_period: str = None) -> ExecutionStrategy:
        """🆕 Stratégie pour les questions de granularité (par heure, par jour, etc.)"""
        
        # Déterminer la période d'analyse selon la granularité
        # Utiliser des périodes qui contiennent des données réelles
        granularity_periods = {
            'hourly': '7d',     # Analyse sur 7 jours pour avoir des données, puis diviser par (7*24)
            'daily': '30d',     # Analyse sur 30 jours pour voir les jours  
            'weekly': '84d',    # Analyse sur 84 jours (12 semaines)
            'monthly': '365d',  # Analyse sur 365 jours (12 mois)
            'yearly': '1825d'   # Analyse sur 1825 jours (5 ans)
        }
        
        analysis_period = granularity_periods.get(validated_period, '7d')
        
        return ExecutionStrategy(
            tool_name='aggregate_granularity',  # 🆕 Nouvel outil spécialisé
            parameters={
                'granularity': validated_period,  # hourly, daily, etc.
                'analysis_period': analysis_period,  # Période d'analyse
                'aggregation': 'avg',  # Moyenne par granularité
                'metric': 'consumption'
            },
            expected_format='granularity',  # 🆕 Nouveau format
            response_template='granularity_response'
        )
    
    def _get_temporal_strategy(self, intent: QuestionIntent, llm_plan: Dict, question: str = "", validated_period: str = None) -> ExecutionStrategy:
        """🆕 Stratégie pour les questions temporelles spécifiques"""
        
        # 🆕 PRIORITÉ: Utiliser la période validée par LangChain si disponible
        if validated_period:
            # Mapper les jours nommés vers des périodes utilisables
            if validated_period in ['saturday', 'sunday']:
                period = '1d'  # Utiliser 1 jour pour les jours spécifiques
            elif validated_period == 'weekend':
                period = '2d'  # Weekend = 2 jours (samedi + dimanche)
                # 🔧 Logique spéciale pour weekend : chercher les derniers samedi + dimanche
                # Pour l'instant, utiliser 2d comme approximation
            else:
                period = validated_period
            # self.logger.info(f"🔍 Utilisation période validée: {period}")  # Logger pas toujours disponible
        # Sinon, déterminer la période selon le temporal (logique existante)
        elif intent.temporal == 'hier':
            period = '1d'
        elif 'mois' in intent.temporal:
            # 🔧 Distinction fine entre différents types de questions "mois"
            question_lower = question.lower() if question else ' '.join(intent.entities).lower()
            
            if 'ce mois-ci' in question_lower or 'ce mois' in question_lower:
                period = 'current_month'  # Mois calendaire actuel
            elif 'mois dernier' in question_lower or 'dernier mois' in question_lower:
                period = 'last_month'     # Mois calendaire précédent
            else:
                period = '30d'            # 30 derniers jours (fallback)
        elif 'heure' in intent.temporal:
            period = '1d'  # Données par heure sur 1 jour
        else:
            period = '7d'
        
        return ExecutionStrategy(
            tool_name='aggregate_temporal',  # 🆕 Nouvel outil
            parameters={
                'period': period,
                'temporal_type': intent.temporal,
                'aggregation': 'sum',
                'metric': 'consumption'
            },
            expected_format='temporal',
            response_template='temporal_response'
        )
    
    def _get_comparaison_strategy(self, intent: QuestionIntent, llm_plan: Dict) -> ExecutionStrategy:
        """🆕 Stratégie intelligente pour les comparaisons"""
        
        # Analyser le type de comparaison selon la question complète
        # (les entités ne contiennent pas toujours les mots-clés de comparaison)
        question_context = self._get_question_context(llm_plan)
        question_lower = question_context.lower()
        
        # Comparaisons saisonnières (été/hiver)
        if any(season in question_lower for season in ['été', 'hiver', 'printemps', 'automne']):
            return ExecutionStrategy(
                tool_name='seasonal_comparison',
                parameters={
                    'comparison_type': 'seasonal',
                    'seasons': self._extract_seasons_from_llm(llm_plan),
                    'metric': 'consumption'
                },
                expected_format='comparison',
                response_template='seasonal_comparison_response'
            )
        
        # Comparaisons temporelles (mois dernier, etc.)
        elif any(temporal in question_lower for temporal in ['dernier', 'précédent']):
            return ExecutionStrategy(
                tool_name='temporal_comparison',
                parameters={
                    'comparison_type': 'temporal',
                    'periods': ['current_month', 'last_month'],
                    'metric': 'consumption'
                },
                expected_format='comparison',
                response_template='temporal_comparison_response'
            )
        
        # Comparaisons weekend/semaine
        elif 'weekend' in question_lower or 'semaine' in question_lower:
            return ExecutionStrategy(
                tool_name='weekday_comparison',
                parameters={
                    'comparison_type': 'weekday',
                    'groups': ['weekend', 'weekday'],
                    'metric': 'consumption'
                },
                expected_format='comparison',
                response_template='weekday_comparison_response'
            )
        
        # Comparaisons de zones (défaut)
        else:
            return ExecutionStrategy(
                tool_name='zone_comparison',
                parameters={
                    'period': '7d',
                    'comparison_type': 'zones'
                },
                expected_format='zones',
                response_template='zone_response'
            )
    
    def _extract_seasons_from_llm(self, llm_plan: Dict) -> list:
        """Extrait les saisons du plan LLM"""
        for step in llm_plan.get('steps', []):
            params = step.get('parameters', {})
            if 'seasons' in params:
                return params['seasons']
        return ['summer', 'winter']  # Par défaut
    
    def _get_question_context(self, llm_plan: Dict) -> str:
        """Récupère le contexte de la question depuis le plan LLM"""
        question_context = llm_plan.get('question_context', '')
        if not question_context:
            # Fallback: analyser les paramètres LLM pour déduire le contexte
            context_parts = []
            for step in llm_plan.get('steps', []):
                params = step.get('parameters', {})
                description = step.get('description', '')
                context_parts.extend([str(v) for v in params.values()])
                context_parts.append(description)
            question_context = ' '.join(context_parts)
        return question_context
    
    def _get_cout_strategy(self, intent: QuestionIntent, llm_plan: Dict) -> ExecutionStrategy:
        """Stratégie pour les questions de coût"""
        return ExecutionStrategy(
            tool_name='cost',
            parameters={
                'period': '7d',
                'calculation_type': 'simple'
            },
            expected_format='cost',
            response_template='cost_response'
        )
    
    def _get_default_strategy(self, intent: QuestionIntent, llm_plan: Dict, validated_period: str = None) -> ExecutionStrategy:
        """Stratégie par défaut avec mapping intelligent des paramètres LLM"""
        # Utiliser le premier step du plan LLM si disponible
        first_step = llm_plan.get('steps', [{}])[0] if llm_plan.get('steps') else {}
        
        # Récupérer les paramètres et les mapper intelligemment
        llm_parameters = first_step.get('parameters', {})
        mapped_parameters = self._map_llm_parameters(llm_parameters)
        
        # 🆕 PRIORITÉ: Utiliser validated_period si disponible
        if validated_period:
            mapped_parameters['period'] = validated_period
        
        return ExecutionStrategy(
            tool_name=first_step.get('tool_name', 'aggregate'),
            parameters=mapped_parameters,
            expected_format='consumption',
            response_template='consumption_response'
        )
    
    def _map_llm_parameters(self, llm_params: Dict) -> Dict:
        """🔧 Mappe les paramètres du LLM vers les paramètres MCP"""
        mapped = llm_params.copy()
        
        # Mapping time_range → period
        if 'time_range' in mapped:
            time_range = mapped.pop('time_range')
            time_range_mapping = {
                'this month': 'current_month',
                'last month': 'last_month',
                'this year': 'current_year', 
                'last year': 'last_year',
                'this week': 'current_week',
                'last week': 'last_week',
                'today': '1d',
                'yesterday': '1d',
                'last 30 days': '30d',
                'last 7 days': '7d'
            }
            mapped['period'] = time_range_mapping.get(time_range, time_range)
        
        # Mapping time_period → period (au cas où)
        if 'time_period' in mapped:
            time_period = mapped.pop('time_period')
            mapped['period'] = time_period
            
        # Assurer qu'il y a toujours une période par défaut
        if 'period' not in mapped:
            mapped['period'] = '7d'
            
        return mapped
    
    def validate_execution_result(self, result: Dict[str, Any], strategy: ExecutionStrategy) -> bool:
        """Valide que le résultat d'exécution est cohérent"""
        if not result or result.get('status') == 'error':
            return False
        
        # Validation selon le format attendu
        if strategy.expected_format == 'moyenne':
            return 'value' in result.get('data', {}) and result['data']['value'] > 0
        elif strategy.expected_format == 'zones':
            return 'zones' in result.get('data', {})
        elif strategy.expected_format == 'cost':
            return 'cost' in result.get('data', {})
        else:
            return True  # Validation basique
    
    def get_fallback_strategy(self, question: str) -> ExecutionStrategy:
        """Stratégie de fallback en cas d'échec"""
        return ExecutionStrategy(
            tool_name='aggregate',
            parameters={'period': '7d', 'aggregation': 'sum'},
            expected_format='consumption',
            response_template='consumption_response'
        )
