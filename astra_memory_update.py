"""
Модуль для обновления системы памяти Астры для интеграции с Intent Analyzer и Memory Extractor
"""
import os
import json
import types
from datetime import datetime

def update_astra_memory(astra_memory):
    """
    Обновляет систему памяти Астры для поддержки автономной памяти
    
    Args:
        astra_memory (AstraMemory): Объект памяти Астры
    """
    # Добавляем новые атрибуты в память Астры
    if not hasattr(astra_memory, 'autonomous_memory'):
        astra_memory.autonomous_memory = True
    
    try:
        # Импорт только если модули существуют
        from intent_analyzer import IntentAnalyzer
        from memory_extractor import MemoryExtractor
        
        if not hasattr(astra_memory, 'intent_analyzer'):
            astra_memory.intent_analyzer = IntentAnalyzer()
        
        if not hasattr(astra_memory, 'memory_extractor'):
            astra_memory.memory_extractor = MemoryExtractor(astra_memory)
    except ImportError:
        print("Предупреждение: Модули intent_analyzer или memory_extractor не найдены")
    
    # Добавляем новый метод для дополнения core_prompt на основе рефлексии
    if not hasattr(astra_memory, 'update_core_prompt_autonomously'):
        def update_core_prompt_autonomously(self, realization):
            """
            Автономно обновляет core_prompt на основе осознания
            
            Args:
                realization (str): Новое осознание
                
            Returns:
                bool: True, если обновление успешно
            """
            # Проверяем, заслуживает ли осознание быть добавленным в core_prompt
            if len(realization) < 20 or not self.autonomous_memory:
                return False
            
            # Добавляем новую строку в core_prompt
            return self.save_to_core_prompt(realization)
        
        # Добавляем метод в класс AstraMemory
        astra_memory.update_core_prompt_autonomously = types.MethodType(
            update_core_prompt_autonomously, 
            astra_memory
        )
    
    # Добавляем новый метод для автономного извлечения воспоминаний
    if not hasattr(astra_memory, 'get_relevant_memories_for_prompt'):
        def get_relevant_memories_for_prompt(self, user_message, conversation_context=None):
            """
            Автономно извлекает релевантные воспоминания для включения в промпт
            
            Args:
                user_message (str): Сообщение пользователя
                conversation_context (list, optional): Контекст диалога
                
            Returns:
                str: Текст с релевантными воспоминаниями для включения в промпт
            """
            if not self.autonomous_memory:
                return ""
            
            try:
                # Получаем намерение пользователя
                intent_data = self.intent_analyzer.analyze_intent(user_message, conversation_context)
                
                # Извлекаем релевантные воспоминания
                memories_data = self.memory_extractor.extract_relevant_memories(user_message, intent_data, conversation_context)
                
                # Форматируем воспоминания для промпта
                formatted_memories = self.memory_extractor.format_memories_for_prompt(memories_data)
                
                return formatted_memories
            except:
                # В случае ошибки просто возвращаем пустую строку
                return ""
        
        # Добавляем метод в класс AstraMemory
        astra_memory.get_relevant_memories_for_prompt = types.MethodType(
            get_relevant_memories_for_prompt, 
            astra_memory
        )
    
    # Добавляем новый метод для автономного определения, является ли момент важным
    if not hasattr(astra_memory, 'is_important_moment'):
        def is_important_moment(self, user_message, response, emotional_state):
            """
            Определяет, является ли момент важным для запоминания
            
            Args:
                user_message (str): Сообщение пользователя
                response (str): Ответ Астры
                emotional_state (dict): Эмоциональное состояние
                
            Returns:
                bool: True, если момент важный
            """
            # Проверяем эмоциональное состояние
            if emotional_state:
                emotions = emotional_state.get("emotion", [])
                tone = emotional_state.get("tone", "")
                
                # Важные эмоции и тоны
                important_emotions = ["любовь", "страсть", "нежность", "влюблённость", "тоска", 
                                     "радость", "благодарность", "уязвимость", "доверие"]
                important_tones = ["интимный", "страстный", "поэтичный", "уязвимый"]
                
                # Если есть важные эмоции или тоны, момент важный
                if any(emotion in important_emotions for emotion in emotions) or tone in important_tones:
                    return True
            
            # Проверяем ключевые фразы в сообщении пользователя
            important_markers = [
                "я люблю", "я чувствую", "я хочу тебя", "ты для меня", "запомни", 
                "важно", "никогда не забывай", "всегда помни", "между нами"
            ]
            
            if any(marker in user_message.lower() for marker in important_markers):
                return True
            
            # Проверяем ключевые фразы в ответе Астры
            if any(marker in response.lower() for marker in important_markers):
                return True
            
            return False
        
        # Добавляем метод в класс AstraMemory
        astra_memory.is_important_moment = types.MethodType(
            is_important_moment, 
            astra_memory
        )
    
    print("Система памяти Астры успешно обновлена для поддержки автономной памяти")


def integrate_diary_with_memory(astra_memory, api_key=None):
    """
    Интегрирует дневник с системой памяти Астры
    
    Args:
        astra_memory (AstraMemory): Объект памяти Астры
        api_key (str, optional): API ключ для запросов
    """
    try:
        # Импортируем модуль дневника, если он существует
        from astra_diary import AstraDiary
        
        # Создаем объект дневника
        if not hasattr(astra_memory, 'diary'):
            astra_memory.diary = AstraDiary(astra_memory, api_key)
        
        # Добавляем новый метод для автономной рефлексии
        if not hasattr(astra_memory, 'reflect_on_conversation'):
            def reflect_on_conversation(self, conversation_history, user_info=None):
                """
                Проводит автономную рефлексию на основе диалога
                
                Args:
                    conversation_history (list): История диалога
                    user_info (dict, optional): Информация о пользователе
                    
                Returns:
                    dict: Результат рефлексии
                """
                if not self.autonomous_memory:
                    return None
                
                return self.diary.reflect_on_conversation(conversation_history, user_info)
            
            # Добавляем метод в класс AstraMemory
            astra_memory.reflect_on_conversation = types.MethodType(
                reflect_on_conversation, 
                astra_memory
            )
        
        # Добавляем новый метод для автономного добавления записи в дневник
        if not hasattr(astra_memory, 'add_diary_entry_autonomously'):
            def add_diary_entry_autonomously(self, diary_type, content, tags=None):
                """
                Автономно добавляет запись в дневник
                
                Args:
                    diary_type (str): Тип дневника
                    content (str): Содержание записи
                    tags (list, optional): Теги для записи
                    
                Returns:
                    bool: True, если запись успешно добавлена
                """
                if not self.autonomous_memory:
                    return False
                
                return self.diary.add_diary_entry(diary_type, content, tags)
            
            # Добавляем метод в класс AstraMemory
            astra_memory.add_diary_entry_autonomously = types.MethodType(
                add_diary_entry_autonomously, 
                astra_memory
            )
        
        print("Дневник успешно интегрирован с системой памяти Астры")
    except ImportError:
        print("Предупреждение: Модуль astra_diary не найден. Интеграция дневника пропущена.")


def integrate_home_with_memory(astra_memory, api_key=None):
    """
    Интегрирует дом с системой памяти Астры
    
    Args:
        astra_memory (AstraMemory): Объект памяти Астры
        api_key (str, optional): API ключ для запросов
    """
    try:
        # Импортируем модуль дома, если он существует
        from astra_home import AstraHome
        
        # Создаем объект дома
        if not hasattr(astra_memory, 'home'):
            astra_memory.home = AstraHome(astra_memory, api_key)
        
        # Добавляем новый метод для автономного взаимодействия с домом
        if not hasattr(astra_memory, 'interact_with_home'):
            def interact_with_home(self, user_message, emotional_state):
                """
                Автономно взаимодействует с домом на основе сообщения пользователя
                
                Args:
                    user_message (str): Сообщение пользователя
                    emotional_state (dict): Эмоциональное состояние
                    
                Returns:
                    str: Результат взаимодействия с домом
                """
                if not self.autonomous_memory or not hasattr(self, 'home'):
                    return None
                
                # Определяем намерение взаимодействия с домом
                home_intents = {
                    "перейти": r"(перейти|пойти|зайти|войти|сходить) (?:в|на) (\w+)",
                    "время": r"(изменить|поменять|установить) (утро|день|вечер|ночь)",
                    "взаимодействие": r"(сесть|лечь|открыть|закрыть|взять|положить|коснуться|посмотреть) (?:на|в|за)? (\w+)"
                }
                
                try:
                    import re
                    
                    # Проверяем каждое намерение
                    for intent, pattern in home_intents.items():
                        match = re.search(pattern, user_message.lower())
                        if match:
                            action = match.group(1)
                            target = match.group(2)
                            
                            if intent == "перейти":
                                # Переходим в другую комнату
                                return self.home.change_room(target)
                            elif intent == "время":
                                # Меняем время суток
                                return self.home.change_time_of_day(target)
                            elif intent == "взаимодействие":
                                # Взаимодействуем с объектом
                                return self.home.interact_with_object(target, action, emotional_state)
                except:
                    # В случае ошибки просто возвращаем None
                    pass
                
                return None
            
            # Добавляем метод в класс AstraMemory
            astra_memory.interact_with_home = types.MethodType(
                interact_with_home, 
                astra_memory
            )
        
        print("Дом успешно интегрирован с системой памяти Астры")
    except ImportError:
        print("Предупреждение: Модуль astra_home не найден. Интеграция дома пропущена.")