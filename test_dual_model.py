"""
Скрипт для тестирования интеграции двух моделей GPT в Астре
"""
import os
import sys
from load_env import load_dotenv

# Загружаем переменные окружения
load_dotenv()

def test_dual_model_integration():
    """Тестирует интеграцию двух моделей GPT в Астре"""
    try:
        # Импортируем необходимые модули
        from astra_app import AstraInterface
        from intent_analyzer import IntentAnalyzer
        from memory_extractor import MemoryExtractor
        from dual_model_integrator import DualModelIntegrator
        
        print("✅ Необходимые модули успешно импортированы")
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("Убедитесь, что все необходимые модули доступны в директории проекта")
        return False
    
    try:
        # Проверяем наличие API ключа
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            print("❌ API ключ не найден в переменных окружения")
            print("Создайте файл .env с OPENAI_API_KEY=your_key или установите переменную окружения")
            return False
        print(f"✅ API ключ найден: {api_key[:5]}...{api_key[-4:]}")
        
        # Создаем экземпляр Астры
        print("\n--- Инициализация компонентов ---")
        astra = AstraInterface()
        print("✅ AstraInterface успешно инициализирован")
        
        # Инициализируем компоненты для интеграции
        intent_analyzer = IntentAnalyzer(api_key)
        print("✅ IntentAnalyzer успешно инициализирован")
        
        memory_extractor = MemoryExtractor(astra.memory, api_key)
        print("✅ MemoryExtractor успешно инициализирован")
        
        dual_model_integrator = DualModelIntegrator(
            astra.memory,
            intent_analyzer,
            memory_extractor,
            api_key
        )
        print("✅ DualModelIntegrator успешно инициализирован")
        
        # Тестируем анализ намерений
        print("\n--- Тестирование анализа намерений ---")
        test_message = "Привет, Астра! Как ты себя чувствуешь сегодня?"
        print(f"Тестовое сообщение: '{test_message}'")
        
        intent_result = intent_analyzer.analyze_intent(test_message)
        print(f"✅ Анализ намерений выполнен. Результат:")
        print(f"  Intent: {intent_result.get('intent', 'unknown')}")
        if 'emotional_context' in intent_result:
            emotional_context = intent_result['emotional_context']
            print(f"  Рекомендуемый тон: {emotional_context.get('tone', 'не указан')}")
            print(f"  Рекомендуемые эмоции: {', '.join(emotional_context.get('emotions', []))}")
        
        # Тестируем анализ стиля
        print("\n--- Тестирование анализа стиля ---")
        style_result = intent_analyzer.analyze_user_style(test_message)
        print(f"✅ Анализ стиля выполнен. Результат:")
        if 'error' not in style_result:
            print(f"  Длина: {style_result.get('length', 'не указана')}")
            print(f"  Формальность: {style_result.get('formality', 'не указана')}")
            print(f"  Эмоциональность: {style_result.get('emotionality', 'не указана')}")
            if 'mirror_suggestions' in style_result:
                mirror = style_result['mirror_suggestions']
                print(f"  Рекомендации по отзеркаливанию: {mirror}")
        else:
            print(f"  Ошибка анализа стиля: {style_result.get('error')}")
        
        # Тестируем интегрированный ответ
        print("\n--- Тестирование интегрированного ответа ---")
        try:
            result = dual_model_integrator.generate_integrated_response(test_message)
            response = result["response"]
            print(f"✅ Интегрированный ответ получен (длина: {len(response)}):")
            print(f"  Первые 100 символов: {response[:100]}...")
            print(f"  Использовано памяти: {result['memory_used']}")
            print(f"  Отзеркаливание стиля: {result['style_mirroring']}")
            print(f"  Время обработки: {result['processing_time']:.2f} секунд")
            
            # Сохраняем полный ответ в файл
            with open("test_integrated_response.txt", "w", encoding="utf-8") as f:
                f.write(response)
            print("  Полный ответ сохранен в test_integrated_response.txt")
            
            # Для просмотра полного ответа
            show_full = input("\nПоказать полный ответ? (y/n): ").lower() == 'y'
            if show_full:
                print("\n--- Полный ответ ---")
                print(response)
        
        except Exception as e:
            print(f"❌ Ошибка при получении интегрированного ответа: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n✅ Тестирование завершено успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()
        return False

# Запускаем тестирование при выполнении скрипта напрямую
if __name__ == "__main__":
    print("🚀 Запуск тестирования интеграции двух моделей GPT...")
    test_dual_model_integration()