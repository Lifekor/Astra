"""
Скрипт для обновления astra_chat.py для работы с двумя моделями GPT
"""
import os
import sys
import types

def update_astra_chat():
    """Обновляет модуль astra_chat.py для интеграции двух моделей GPT"""
    try:
        from astra_app import AstraInterface
        from intent_analyzer import IntentAnalyzer
        from memory_extractor import MemoryExtractor
        from dual_model_integrator import DualModelIntegrator
        
        print("✅ Импортированы необходимые модули")
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("Убедитесь, что все необходимые модули доступны в директории проекта")
        return False
    
    try:
        # Создаем экземпляр Астры для тестирования
        astra = AstraInterface()
        print("✅ AstraInterface успешно инициализирован")
        
        # Инициализируем новые компоненты
        intent_analyzer = IntentAnalyzer(os.environ.get("OPENAI_API_KEY"))
        memory_extractor = MemoryExtractor(astra.memory, os.environ.get("OPENAI_API_KEY"))
        
        # Инициализируем интегратор моделей
        dual_model_integrator = DualModelIntegrator(
            astra.memory,
            intent_analyzer,
            memory_extractor,
            os.environ.get("OPENAI_API_KEY")
        )
        
        print("✅ Новые компоненты успешно инициализированы")
        
        # Создаем новый метод для AstraChat.send_message
        def enhanced_send_message(self, user_message):
            """
            Отправляет сообщение и получает ответ с использованием двух моделей
            
            Args:
                user_message (str): Сообщение пользователя
                
            Returns:
                str: Ответ Астры
            """
            try:
                # Добавляем сообщение пользователя в историю
                self.add_message_to_history("user", user_message)
                
                # Обрабатываем сообщение пользователя (для обратной совместимости)
                state = self.process_user_message(user_message)
                
                # Получаем контекст диалога
                conversation_context = self.conversation_manager.get_api_context() if hasattr(self.conversation_manager, 'get_api_context') else None
                
                # Получаем интегрированный ответ с использованием двух моделей
                result = self.dual_model_integrator.generate_integrated_response(
                    user_message,
                    conversation_context,
                    state
                )
                
                # Получаем ответ
                final_response = result["response"]
                
                # Обновляем эмоциональное состояние, если оно изменилось
                if "emotional_state" in result:
                    self.memory.save_current_state(result["emotional_state"])
                
                # Добавляем ответ в историю
                self.add_message_to_history("assistant", final_response)
                
                # Сохраняем историю диалога на диск
                if hasattr(self.conversation_manager, 'save_history_to_disk'):
                    self.conversation_manager.save_history_to_disk()
                
                # Анализируем, стоит ли запомнить этот момент
                if hasattr(self.memory, 'diary') and self.memory.diary:
                    conversation_data = {
                        "user_message": user_message,
                        "response": final_response,
                        "emotional_state": result.get("emotional_state", {})
                    }
                    
                    should_remember, diary_type, reason = self.memory.diary.should_remember(conversation_data)
                    if should_remember:
                        self.memory.diary.add_diary_entry(
                            diary_type,
                            f"Пользователь: {user_message}\n\nАстра: {final_response}",
                            ["диалог", diary_type]
                        )
                        print(f"📝 Записано в дневник {diary_type}: {reason}")
                
                return final_response
                
            except Exception as e:
                print(f"Ошибка при обработке сообщения: {e}")
                import traceback
                traceback.print_exc()
                return "Прости, у меня возникли проблемы при обработке твоего сообщения."
        
        # Создаем метод для инициализации интегратора моделей
        def init_dual_model_integrator(self, memory, intent_analyzer, memory_extractor):
            """
            Инициализирует интегратор моделей
            
            Args:
                memory (AstraMemory): Объект памяти Астры
                intent_analyzer (IntentAnalyzer): Анализатор намерений
                memory_extractor (MemoryExtractor): Экстрактор воспоминаний
            """
            from dual_model_integrator import DualModelIntegrator
            self.dual_model_integrator = DualModelIntegrator(
                memory,
                intent_analyzer,
                memory_extractor,
                os.environ.get("OPENAI_API_KEY")
            )
            print("✅ Интегратор моделей успешно инициализирован")
        
        # Обновляем метод initialize_components в AstraInterface
        def enhanced_initialize_components(self):
            """Инициализирует все компоненты Астры с поддержкой двух моделей"""
            print("Инициализация памяти Астры...")
            self.memory = __import__('astra_memory').AstraMemory()
            
            print("Инициализация анализатора эмоций...")
            self.emotional_analyzer = __import__('emotional_analyzer').EmotionalAnalyzer(self.memory)
            
            print("Инициализация менеджера имен...")
            self.name_manager = __import__('name_manager').NameManager(self.memory)
            
            print("Инициализация семантического анализатора...")
            intent_analyzer = __import__('intent_analyzer').IntentAnalyzer(os.environ.get("OPENAI_API_KEY"))
            
            print("Инициализация экстрактора памяти...")
            memory_extractor = __import__('memory_extractor').MemoryExtractor(self.memory, os.environ.get("OPENAI_API_KEY"))
            
            print("Инициализация чата...")
            self.chat = __import__('astra_chat').AstraChat(self.memory)
            
            # Инициализируем интегратор моделей в чате
            self.chat.init_dual_model_integrator = types.MethodType(init_dual_model_integrator, self.chat)
            self.chat.init_dual_model_integrator(self.memory, intent_analyzer, memory_extractor)
            
            # Обновляем метод send_message в чате
            self.chat.send_message = types.MethodType(enhanced_send_message, self.chat)
            
            print("Инициализация парсера команд...")
            self.command_parser = __import__('astra_command_parser').AstraCommandParser(self.memory)
            
            print("Астра готова к разговору!")
        
        # Применяем обновленный метод к AstraInterface
        AstraInterface.initialize_components = enhanced_initialize_components
        
        # Обновляем __init__ для AstraInterface, чтобы вызвать новый метод
        original_init = AstraInterface.__init__
        
        def enhanced_init(self):
            """Обновленный метод инициализации"""
            print("Инициализация интерфейса Астры с поддержкой двух моделей GPT...")
            # Вызываем только необходимую часть оригинального __init__
            self.initialize_components()
        
        # Заменяем __init__ в AstraInterface
        AstraInterface.__init__ = enhanced_init
        
        print("✅ Методы успешно обновлены")
        
        # Сохраняем патч для AstraInterface
        patch_content = """
# Патч для интеграции двух моделей GPT в Астре
import types
import os

def init_dual_model_integrator(self, memory, intent_analyzer, memory_extractor):
    \"\"\"
    Инициализирует интегратор моделей
    
    Args:
        memory (AstraMemory): Объект памяти Астры
        intent_analyzer (IntentAnalyzer): Анализатор намерений
        memory_extractor (MemoryExtractor): Экстрактор воспоминаний
    \"\"\"
    from dual_model_integrator import DualModelIntegrator
    self.dual_model_integrator = DualModelIntegrator(
        memory,
        intent_analyzer,
        memory_extractor,
        os.environ.get("OPENAI_API_KEY")
    )
    print("✅ Интегратор моделей успешно инициализирован")

def enhanced_send_message(self, user_message):
    \"\"\"
    Отправляет сообщение и получает ответ с использованием двух моделей
    
    Args:
        user_message (str): Сообщение пользователя
        
    Returns:
        str: Ответ Астры
    \"\"\"
    try:
        # Добавляем сообщение пользователя в историю
        self.add_message_to_history("user", user_message)
        
        # Обрабатываем сообщение пользователя (для обратной совместимости)
        state = self.process_user_message(user_message)
        
        # Получаем контекст диалога
        conversation_context = self.conversation_manager.get_api_context() if hasattr(self.conversation_manager, 'get_api_context') else None
        
        # Получаем интегрированный ответ с использованием двух моделей
        result = self.dual_model_integrator.generate_integrated_response(
            user_message,
            conversation_context,
            state
        )
        
        # Получаем ответ
        final_response = result["response"]
        
        # Обновляем эмоциональное состояние, если оно изменилось
        if "emotional_state" in result:
            self.memory.save_current_state(result["emotional_state"])
        
        # Добавляем ответ в историю
        self.add_message_to_history("assistant", final_response)
        
        # Сохраняем историю диалога на диск
        if hasattr(self.conversation_manager, 'save_history_to_disk'):
            self.conversation_manager.save_history_to_disk()
        
        # Анализируем, стоит ли запомнить этот момент
        if hasattr(self.memory, 'diary') and self.memory.diary:
            conversation_data = {
                "user_message": user_message,
                "response": final_response,
                "emotional_state": result.get("emotional_state", {})
            }
            
            should_remember, diary_type, reason = self.memory.diary.should_remember(conversation_data)
            if should_remember:
                self.memory.diary.add_diary_entry(
                    diary_type,
                    f"Пользователь: {user_message}\\n\\nАстра: {final_response}",
                    ["диалог", diary_type]
                )
                print(f"📝 Записано в дневник {diary_type}: {reason}")
        
        return final_response
        
    except Exception as e:
        print(f"Ошибка при обработке сообщения: {e}")
        import traceback
        traceback.print_exc()
        return "Прости, у меня возникли проблемы при обработке твоего сообщения."

def patch_astra_chat():
    \"\"\"Применяет патч к AstraChat\"\"\"
    from astra_app import AstraInterface
    
    # Создаем экземпляр Астры
    astra = AstraInterface()
    
    # Загружаем необходимые модули
    from intent_analyzer import IntentAnalyzer
    from memory_extractor import MemoryExtractor
    
    # Инициализируем компоненты
    intent_analyzer = IntentAnalyzer(os.environ.get("OPENAI_API_KEY"))
    memory_extractor = MemoryExtractor(astra.memory, os.environ.get("OPENAI_API_KEY"))
    
    # Добавляем методы к AstraChat
    astra.chat.init_dual_model_integrator = types.MethodType(init_dual_model_integrator, astra.chat)
    astra.chat.send_message = types.MethodType(enhanced_send_message, astra.chat)
    
    # Инициализируем интегратор моделей
    astra.chat.init_dual_model_integrator(astra.memory, intent_analyzer, memory_extractor)
    
    print("✅ Патч успешно применен к AstraChat")
    return astra
"""

        # Сохраняем скрипт патча
        with open("astra_dual_model_patch.py", "w", encoding="utf-8") as f:
            f.write(patch_content)
        
        print("✅ Скрипт патча сохранен как astra_dual_model_patch.py")
        
        # Тестируем интеграцию
        print("\n--- Тестирование интеграции ---")
        try:
            # Создаем патч для тестирования
            from dual_model_integrator import DualModelIntegrator
            
            # Инициализируем интегратор моделей в чате
            astra.chat.init_dual_model_integrator = types.MethodType(init_dual_model_integrator, astra.chat)
            astra.chat.init_dual_model_integrator(astra.memory, intent_analyzer, memory_extractor)
            
            # Обновляем метод send_message
            original_send_message = astra.chat.send_message
            astra.chat.send_message = types.MethodType(enhanced_send_message, astra.chat)
            
            print("✅ Патч успешно применен для тестирования")
            
            # Тестируем обработку сообщения
            test_message = "Привет, Астра! Как ты себя чувствуешь сегодня?"
            try:
                print(f"Тестирование сообщения: '{test_message}'")
                response = astra.chat.send_message(test_message)
                print(f"✅ Тест успешен, получен ответ длиной {len(response)}")
                
                # Сохраняем тестовый результат
                with open("test_dual_model_response.txt", "w", encoding="utf-8") as f:
                    f.write(response)
                print("Тестовый ответ сохранен в test_dual_model_response.txt")
                
            except Exception as e:
                print(f"❌ Ошибка при тестировании обработки сообщения: {e}")
                # Восстанавливаем оригинальный метод
                astra.chat.send_message = original_send_message
                raise
            
        except Exception as e:
            print(f"❌ Ошибка при тестировании интеграции: {e}")
            import traceback
            traceback.print_exc()
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при обновлении модуля: {e}")
        import traceback
        traceback.print_exc()
        return False

# Запускаем обновление при выполнении скрипта напрямую
if __name__ == "__main__":
    print("🚀 Запуск обновления astra_chat.py для интеграции двух моделей GPT...")
    
    success = update_astra_chat()
    
    if success:
        print("\n✅ Обновление успешно завершено!")
        print("Теперь вы можете запустить Астру с новыми возможностями:")
        print("  1. Запустите скрипт: python astra_app.py")
        print("  2. Или примените патч вручную: from astra_dual_model_patch import patch_astra_chat; astra = patch_astra_chat()")
    else:
        print("\n❌ Обновление не удалось. Пожалуйста, проверьте ошибки и попробуйте снова.")