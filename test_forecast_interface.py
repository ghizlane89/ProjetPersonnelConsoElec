#!/usr/bin/env python3
"""
Test de l'interface de prévisions
"""

from forecast_interface import forecast_tool

def test_forecast_interface():
    """
    Test complet de l'interface de prévisions
    """
    print("🧪 TEST DE L'INTERFACE DE PRÉVISIONS")
    print("=" * 50)
    
    # Test 1: Statut initial
    print("\n1. 📊 Statut initial")
    status = forecast_tool.get_status()
    print(f"   Mode actuel : {status['current_mode']}")
    print(f"   Contexte : {status['context']['mode']}")
    
    # Test 2: Prévisions 1 jour
    print("\n2. 🔮 Prévisions 1 jour")
    result_1d = forecast_tool.generate_forecast("1d", "simple")
    print(f"   Statut : {result_1d['status']}")
    print(f"   Mode : {result_1d['mode']}")
    print(f"   Prédictions : {len(result_1d['predictions'])} points")
    print(f"   Premier point : {result_1d['predictions'][0]}")
    
    # Test 3: Prévisions 7 jours
    print("\n3. 🔮 Prévisions 7 jours")
    result_7d = forecast_tool.generate_forecast("7d", "simple")
    print(f"   Statut : {result_7d['status']}")
    print(f"   Prédictions : {len(result_7d['predictions'])} points")
    
    # Test 4: Prévisions 30 jours
    print("\n4. 🔮 Prévisions 30 jours")
    result_30d = forecast_tool.generate_forecast("30d", "simple")
    print(f"   Statut : {result_30d['status']}")
    print(f"   Prédictions : {len(result_30d['predictions'])} points")
    
    # Test 5: Changement de mode
    print("\n5. 🔄 Test changement de mode")
    switch_result = forecast_tool.switch_mode("prophet")
    print(f"   Résultat : {switch_result}")
    
    # Test 6: Prévisions Prophet (non implémenté)
    print("\n6. 🤖 Test Prophet (non implémenté)")
    prophet_result = forecast_tool.generate_forecast("1d", "simple")
    print(f"   Statut : {prophet_result['status']}")
    print(f"   Message : {prophet_result['message']}")
    
    # Retour au mode mock
    forecast_tool.switch_mode("mock")
    
    print("\n" + "=" * 50)
    print("✅ TEST TERMINÉ")

if __name__ == "__main__":
    test_forecast_interface()




