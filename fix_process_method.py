"""
Скрипт исправления метода process_message
"""
import types

def fix_process_message():
    try:
        from astra_app import AstraInterface
        
        # Создаем экземпляр Астры
        astra = AstraInterface()
        print("✅ AstraInterface успешно инициализирован")
        
        # Правильное переопределение метода process_message
        original_process_message = astra.process_message
        
        def enhanced_process_message(self, message):
            """
            Обрабатывает сообщение пользователя с визуальным форматированием
            
            Args:
                message (str): Сообщение пользователя
                
            Returns:
                str: Отформатированный ответ Астры
            """
            # Получаем базовый ответ через оригинальный метод (правильно вызываем)
            response = original_process_message(message)
            
            # Форматируем с эмоциями, если есть визуализатор
            if hasattr(self, 'visualizer') and hasattr(self, 'format_response_with_emotions'):
                try:
                    return self.format_response_with_emotions(response, self.memory.current_state)
                except Exception as e:
                    print(f"Ошибка при форматировании ответа: {e}")
            
            return response
        
        # Заменяем метод
        astra.process_message = types.MethodType(
            enhanced_process_message, 
            astra
        )
        print("✅ Метод process_message исправлен")
        
        # Тестируем
        print("Тестирование метода process_message...")
        test_response = astra.process_message("Привет, Астра! Ты меня помнишь?")
        
        print(f"✅ Тест успешен, получен ответ длиной {len(test_response)}")
        
        # Сохраняем для проверки
        with open("test_response.txt", "w", encoding="utf-8") as f:
            f.write(test_response)
        
        print("Ответ сохранен в test_response.txt для проверки")
        
        print("\n✨ Исправление завершено!")
        print("Перезапустите Астру командой: python astra_app.py")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_process_message()