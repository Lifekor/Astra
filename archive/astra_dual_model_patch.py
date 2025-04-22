
# Патч для интеграции двух моделей GPT в Астре
import types
import os

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

def patch_astra_chat():
    """Применяет патч к AstraChat"""
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
