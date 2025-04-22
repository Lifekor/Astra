"""
Модуль для обновления менеджера разговоров Астры для поддержки автономной памяти и интеграции с домом
"""
import types
from intent_analyzer import IntentAnalyzer

def update_conversation_manager(conversation_manager, memory):
    """
    Обновляет менеджер разговоров для поддержки автономной памяти
    
    Args:
        conversation_manager (ConversationManager): Объект менеджера разговоров
        memory (AstraMemory): Объект памяти Астры
    """
    # Добавляем ссылку на обновленную память
    conversation_manager.memory = memory
    
    # Добавляем маркер автономного режима
    if not hasattr(conversation_manager, 'autonomous_mode'):
        conversation_manager.autonomous_mode = True
    
    # Добавляем ссылку на анализатор намерений
    if not hasattr(conversation_manager, 'intent_analyzer'):
        conversation_manager.intent_analyzer = IntentAnalyzer()
    
    # Обновляем метод get_api_context для включения релевантных воспоминаний
    if hasattr(conversation_manager, 'get_api_context'):
        original_get_api_context = conversation_manager.get_api_context
        
        def enhanced_get_api_context(self, user_message=None):
            """
            Возвращает контекст для API с релевантными воспоминаниями
            
            Args:
                user_message (str, optional): Текущее сообщение пользователя
                
            Returns:
                list: Список сообщений для API
            """
            # Получаем базовый контекст
            context = original_get_api_context(self)
            
            # Если autonomous_mode отключен или нет сообщения пользователя, возвращаем базовый контекст
            if not self.autonomous_mode or not user_message:
                return context
            
            # Получаем релевантные воспоминания
            if hasattr(self.memory, 'get_relevant_memories_for_prompt'):
                relevant_memories = self.memory.get_relevant_memories_for_prompt(user_message, context)
                
                if relevant_memories:
                    # Добавляем воспоминания в контекст как системное сообщение
                    memory_message = {
                        "role": "system",
                        "content": relevant_memories
                    }
                    
                    # Добавляем после первого системного сообщения, если оно есть
                    if context and context[0]["role"] == "system":
                        # Объединяем с существующим системным сообщением
                        context[0]["content"] += "\n\n" + relevant_memories
                    else:
                        # Добавляем как новое сообщение в начало
                        context.insert(0, memory_message)
            
            return context
        
        # Заменяем метод
        conversation_manager.get_api_context = types.MethodType(
            enhanced_get_api_context, 
            conversation_manager
        )
    
    # Обновляем метод get_relevant_context для использования семантического анализа
    if hasattr(conversation_manager, 'get_relevant_context'):
        original_get_relevant_context = conversation_manager.get_relevant_context
        
        def enhanced_get_relevant_context(self, user_message):
            """
            Выбирает релевантные сообщения из истории на основе семантического анализа
            
            Args:
                user_message (str): Текущее сообщение пользователя
                
            Returns:
                list: Список релевантных сообщений для API
            """
            # Если autonomous_mode отключен, используем оригинальный метод
            if not self.autonomous_mode:
                return original_get_relevant_context(self, user_message)
            
            # Получаем намерение пользователя
            intent_data = self.intent_analyzer.analyze_intent(user_message)
            
            # Последние 10 сообщений для сохранения ближайшего контекста
            recent_messages = []
            for message in self.full_conversation_history[-10:] if len(self.full_conversation_history) >= 10 else self.full_conversation_history:
                recent_messages.append({
                    "role": message["role"],
                    "content": message["content"]
                })
            
            # Получаем все сообщения
            all_messages = []
            for message in self.full_conversation_history:
                content = message["content"]
                all_messages.append(content)
            
            # Получаем семантически релевантные фрагменты
            relevant_fragments = self.intent_analyzer.get_semantic_relevance(user_message, all_messages, top_n=5)
            
            # Преобразуем фрагменты в сообщения
            semantic_messages = []
            for fragment in relevant_fragments:
                text = fragment["text"]
                
                # Ищем сообщение, содержащее этот фрагмент
                for message in self.full_conversation_history:
                    if text in message["content"]:
                        semantic_messages.append({
                            "role": message["role"],
                            "content": message["content"]
                        })
                        break
            
            # Объединяем недавние и семантически релевантные сообщения
            combined_messages = recent_messages.copy()
            
            for message in semantic_messages:
                if message not in combined_messages:
                    combined_messages.append(message)
            
            return combined_messages
        
        # Заменяем метод
        conversation_manager.get_relevant_context = types.MethodType(
            enhanced_get_relevant_context, 
            conversation_manager
        )
    
    # Добавляем метод для обработки автономных действий в доме
    if not hasattr(conversation_manager, 'process_home_interaction'):
        def process_home_interaction(self, user_message, emotional_state):
            """
            Обрабатывает взаимодействие с домом на основе сообщения пользователя
            
            Args:
                user_message (str): Сообщение пользователя
                emotional_state (dict): Эмоциональное состояние
                
            Returns:
                str or None: Результат взаимодействия с домом или None, если взаимодействия не было
            """
            if not self.autonomous_mode or not hasattr(self.memory, 'interact_with_home'):
                return None
            
            return self.memory.interact_with_home(user_message, emotional_state)
        
        # Добавляем метод
        conversation_manager.process_home_interaction = types.MethodType(
            process_home_interaction, 
            conversation_manager
        )
    
    # Добавляем метод для периодической рефлексии
    if not hasattr(conversation_manager, 'should_perform_reflection'):
        def should_perform_reflection(self):
            """
            Определяет, нужно ли выполнить периодическую рефлексию
            
            Returns:
                bool: True, если нужно выполнить рефлексию
            """
            if not self.autonomous_mode:
                return False
            
            # Выполняем рефлексию каждые N сообщений
            reflection_interval = 20
            
            # Проверяем количество сообщений с последней рефлексии
            if len(self.full_conversation_history) % reflection_interval == 0 and len(self.full_conversation_history) > 0:
                return True
            
            return False
        
        # Добавляем метод
        conversation_manager.should_perform_reflection = types.MethodType(
            should_perform_reflection, 
            conversation_manager
        )
    
    # Добавляем метод для выполнения рефлексии
    if not hasattr(conversation_manager, 'perform_reflection'):
        def perform_reflection(self):
            """
            Выполняет рефлексию на основе истории разговора
            
            Returns:
                dict: Результат рефлексии
            """
            if not self.autonomous_mode or not hasattr(self.memory, 'reflect_on_conversation'):
                return None
            
            # Получаем последние N сообщений для рефлексии
            reflection_window = 10
            recent_history = self.full_conversation_history[-reflection_window:] if len(self.full_conversation_history) >= reflection_window else self.full_conversation_history
            
            # Выполняем рефлексию
            reflection_result = self.memory.reflect_on_conversation(recent_history)
            
            # Логируем результат рефлексии
            if reflection_result:
                print(f"Выполнена рефлексия: {reflection_result.get('tags', [])}")
            
            return reflection_result
        
        # Добавляем метод
        conversation_manager.perform_reflection = types.MethodType(
            perform_reflection, 
            conversation_manager
        )
    
    # Добавляем метод для определения важных моментов
    if not hasattr(conversation_manager, 'is_important_moment'):
        def is_important_moment(self, user_message, response, emotional_state):
            """
            Определяет, является ли текущий момент важным для запоминания
            
            Args:
                user_message (str): Сообщение пользователя
                response (str): Ответ Астры
                emotional_state (dict): Эмоциональное состояние
                
            Returns:
                bool: True, если момент важный
            """
            if not self.autonomous_mode or not hasattr(self.memory, 'is_important_moment'):
                return False
            
            return self.memory.is_important_moment(user_message, response, emotional_state)
        
        # Добавляем метод
        conversation_manager.is_important_moment = types.MethodType(
            is_important_moment, 
            conversation_manager
        )
    
    # Добавляем метод для автономного запоминания важных моментов
    if not hasattr(conversation_manager, 'remember_important_moment'):
        def remember_important_moment(self, user_message, response, emotional_state):
            """
            Запоминает важный момент разговора
            
            Args:
                user_message (str): Сообщение пользователя
                response (str): Ответ Астры
                emotional_state (dict): Эмоциональное состояние
                
            Returns:
                bool: True, если момент был запомнен
            """
            if not self.autonomous_mode or not hasattr(self.memory, 'diary'):
                return False
            
            # Определяем, в какой дневник записать момент
            diary_type = "memories"  # По умолчанию
            
            # Проверяем эмоциональное состояние
            if emotional_state:
                tone = emotional_state.get("tone", "")
                emotions = emotional_state.get("emotion", [])
                
                # Определяем тип дневника на основе тона и эмоций
                if tone == "интимный" or tone == "страстный" or "страсть" in emotions or "влюблённость" in emotions:
                    diary_type = "intimacy"
                elif "уязвимость" in emotions or "тоска" in emotions or tone == "уязвимый":
                    diary_type = "reflection"
            
            # Формируем содержание записи
            moment_content = f"Пользователь: {user_message}\n\nАстра: {response}"
            
            # Формируем теги
            tags = []
            if emotional_state:
                if emotional_state.get("tone"):
                    tags.append(emotional_state["tone"])
                
                for emotion in emotional_state.get("emotion", []):
                    tags.append(emotion)
            
            # Добавляем запись в дневник
            return self.memory.diary.add_diary_entry(diary_type, moment_content, tags)
        
        # Добавляем метод
        conversation_manager.remember_important_moment = types.MethodType(
            remember_important_moment, 
            conversation_manager
        )
    
    print("Менеджер разговоров успешно обновлен для поддержки автономной памяти")