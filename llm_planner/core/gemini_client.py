#!/usr/bin/env python3
"""
🤖 CLIENT GEMINI - CONFIGURATION API LLM
=======================================

Client pour l'API Google Gemini 1.5 Flash.
Gestion des appels API avec cache intelligent.

Critères d'acceptation :
- Cache actif
- Aucune exécution côté LLM
- Gestion d'erreurs robuste
"""

import os
import json
import time
import hashlib
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import google.generativeai as genai

# Chargement des variables d'environnement
load_dotenv()

class GeminiClient:
    """Client pour l'API Google Gemini 1.5 Flash"""
    
    def __init__(self):
        """Initialisation du client Gemini"""
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY non trouvée dans les variables d'environnement")
        
        # Configuration de l'API
        genai.configure(api_key=self.api_key)
        
        # Modèle Gemini 1.5 Flash
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Cache en mémoire (simple)
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = 3600  # 1 heure par défaut
        
        print("✅ Client Gemini 1.5 Flash initialisé")
    
    def _generate_cache_key(self, prompt: str) -> str:
        """Génère une clé de cache pour un prompt"""
        return hashlib.md5(prompt.encode()).hexdigest()
    
    def _extract_question_from_prompt(self, prompt: str) -> str:
        """Extrait la question du prompt pour le contexte"""
        # Chercher la ligne "Question utilisateur :"
        lines = prompt.split('\n')
        for line in lines:
            if line.startswith('Question utilisateur :'):
                return line.replace('Question utilisateur :', '').strip().strip('"')
        return ""
    
    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Vérifie si une entrée de cache est valide"""
        if 'timestamp' not in cache_entry:
            return False
        
        age = time.time() - cache_entry['timestamp']
        return age < self._cache_ttl
    
    def generate_plan(self, question: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Génère un plan JSON pour une question donnée
        
        Args:
            question: Question de l'utilisateur
            use_cache: Utiliser le cache si disponible
            
        Returns:
            Plan JSON généré par le LLM
        """
        # Génération du prompt
        from llm_planner.prompts.plan_generator_prompt import format_plan_prompt
        prompt = format_plan_prompt(question)
        
        # Vérification du cache
        if use_cache:
            cache_key = self._generate_cache_key(prompt)
            if cache_key in self._cache:
                cache_entry = self._cache[cache_key]
                if self._is_cache_valid(cache_entry):
                    print(f"✅ Plan récupéré du cache (âge: {time.time() - cache_entry['timestamp']:.1f}s)")
                    return cache_entry['plan']
                else:
                    # Supprimer l'entrée expirée
                    del self._cache[cache_key]
        
        try:
            print("🤖 Génération d'un nouveau plan avec Gemini...")
            start_time = time.time()
            
            # Appel à l'API Gemini
            response = self.model.generate_content(prompt)
            
            generation_time = time.time() - start_time
            print(f"✅ Plan généré en {generation_time:.2f}s")
            
            # Parsing de la réponse JSON
            try:
                # Extraire le JSON de la réponse
                response_text = response.text.strip()
                
                # Nettoyer la réponse si nécessaire
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                
                plan = json.loads(response_text)
                
                # Ajouter le contexte de la question
                plan["question_context"] = self._extract_question_from_prompt(prompt)
                
                # Mise en cache
                if use_cache:
                    cache_key = self._generate_cache_key(prompt)
                    self._cache[cache_key] = {
                        'plan': plan,
                        'timestamp': time.time(),
                        'generation_time': generation_time
                    }
                    print(f"💾 Plan mis en cache (clé: {cache_key[:8]}...)")
                
                return plan
                
            except json.JSONDecodeError as e:
                print(f"❌ Erreur de parsing JSON: {e}")
                print(f"Réponse brute: {response.text}")
                raise ValueError(f"Réponse LLM non-JSON valide: {e}")
                
        except Exception as e:
            print(f"❌ Erreur lors de la génération du plan: {e}")
            raise
    
    def validate_plan(self, plan: Dict[str, Any]) -> bool:
        """
        Valide un plan avec le schéma Pydantic
        
        Args:
            plan: Plan à valider
            
        Returns:
            True si le plan est valide
        """
        try:
            from llm_planner.models.plan_schema import LLMPlan
            LLMPlan(**plan)
            return True
        except Exception as e:
            print(f"❌ Plan invalide: {e}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du cache"""
        total_entries = len(self._cache)
        valid_entries = sum(1 for entry in self._cache.values() if self._is_cache_valid(entry))
        
        return {
            'total_entries': total_entries,
            'valid_entries': valid_entries,
            'expired_entries': total_entries - valid_entries,
            'cache_size_mb': sum(len(json.dumps(entry)) for entry in self._cache.values()) / (1024 * 1024)
        }
    
    def clear_cache(self):
        """Vide le cache"""
        self._cache.clear()
        print("🗑️ Cache vidé")
    
    def set_cache_ttl(self, ttl_seconds: int):
        """Définit la durée de vie du cache"""
        self._cache_ttl = ttl_seconds
        print(f"⏰ TTL du cache défini à {ttl_seconds} secondes")

# Instance globale du client
_gemini_client: Optional[GeminiClient] = None

def get_gemini_client() -> GeminiClient:
    """Retourne l'instance globale du client Gemini"""
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client
