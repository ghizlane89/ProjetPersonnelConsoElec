#!/usr/bin/env python3
"""
🤖 CLIENT GEMINI AGENTIQUE - TRADUCTEUR SIMPLE
=============================================

Client minimal pour l'API Google Gemini 1.5 Flash.
Rôle : Traducteur question → JSON simple.
L'orchestrateur gère la complexité.
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
    """Client agentique pour Gemini - Traduction simple"""
    
    def __init__(self):
        """Initialisation minimaliste"""
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY manquante")
        
        # Configuration API
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Cache simple
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = 3600  # 1 heure
        

    
    def _generate_cache_key(self, prompt: str) -> str:
        """Génère clé de cache"""
        return hashlib.md5(prompt.encode()).hexdigest()
    
    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Vérifie validité du cache"""
        if 'timestamp' not in cache_entry:
            return False
        age = time.time() - cache_entry['timestamp']
        return age < self._cache_ttl
    
    def generate_plan(self, question: str, use_cache: bool = True) -> Dict[str, Any]:
        """Traduit question → plan JSON"""
        from llm_planner.prompts.plan_generator_prompt import format_plan_prompt
        prompt = format_plan_prompt(question)
        
        # Cache
        if use_cache:
            cache_key = self._generate_cache_key(prompt)
            if cache_key in self._cache:
                cache_entry = self._cache[cache_key]
                if self._is_cache_valid(cache_entry):
                    return cache_entry['plan']
                else:
                    del self._cache[cache_key]
        
        try:
            # Appel API
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Nettoyer JSON
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            plan = json.loads(response_text)
            plan["question_context"] = question
            
            # Cache
            if use_cache:
                self._cache[self._generate_cache_key(prompt)] = {
                    'plan': plan,
                    'timestamp': time.time()
                }
            
            return plan
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Réponse non-JSON: {e}")
        except Exception as e:
            print(f"❌ Erreur traduction: {e}")
            raise
    
    def validate_plan(self, plan: Dict[str, Any]) -> bool:
        """Validation basique - L'orchestrateur fera le reste"""
        try:
            from llm_planner.models.plan_schema import LLMPlan
            LLMPlan(**plan)
            return True
        except Exception as e:
            print(f"❌ Plan invalide: {e}")
            return False
    
    def clear_cache(self):
        """Vide le cache"""
        self._cache.clear()

# Instance globale
_gemini_client: Optional[GeminiClient] = None

def get_gemini_client() -> GeminiClient:
    """Retourne l'instance globale"""
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client