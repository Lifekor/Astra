"""
Патч для улучшения интеграции компонентов памяти Астры с двухмодельной системой
Решает проблему отсутствия воспоминаний и потери эмоционального контекста
"""
import os
import sys
import types
import json

def apply_memory_integration_patch():
    """Применяет патч для улучшения интеграции компонентов памяти"""
    try:
        # Импортируем необходимые модули
        from dual_model_integrator import DualModelIntegrator
        from memory_extractor import MemoryExtractor
        from astra_app import AstraInterface
        
        print("✅ Необходимые модули импортированы")
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("Убедитесь, что все необходимые модули доступны в директории проекта")
        return False
    
    # 1. Патч для DualModelIntegrator - улучшение работы с памятью и эмоциями
    def enhanced_generate_integrated_response(self, user_message, conversation_context=None, emotional_state=None, temperature=None):
        """
        Улучшенная версия generate_integrated_response с лучшей работой с памятью
        """
        import time
        
        start_time = time.time()
        
        # Шаг 1: Определяем намерение пользователя с помощью gpt-4
        intent_data = self.intent_analyzer.analyze_intent(user_message, conversation_context)
        self.last_intent_data = intent_data
        
        # Логирование намерения
        self.log_step("1. Intent Analysis", intent_data)
        
        # Шаг 2: Анализируем стиль пользователя
        previous_user_messages = []
        if conversation_context:
            previous_user_messages = [msg["content"] for msg in conversation_context[-5:] if msg["role"] == "user"]
        
        style_data = self.intent_analyzer.analyze_user_style(user_message, previous_user_messages)
        self.last_style_data = style_data
        
        # Логирование анализа стиля
        self.log_step("2. Style Analysis", style_data)
        
        # НОВОЕ: Проверяем наличие триггеров памяти
        should_trigger_memory = check_memory_triggers(user_message, self.memory)
        intent_type = intent_data.get("intent", "")
        
        # Типы намерений, которые должны активировать воспоминания
        memory_activating_intents = [
            "about_relationship", "about_astra", "intimate", 
            "memory_recall", "emotional_support"
        ]
        
        # Активируем воспоминания на основе интента
        if intent_type in memory_activating_intents:
            should_trigger_memory = True
        
        # НОВОЕ: Активация по эмоциональному контексту
        if "emotional_context" in intent_data and intent_data["emotional_context"]:
            emotions = intent_data["emotional_context"].get("emotions", [])
            deep_emotions = ["любовь", "тоска", "нежность", "уязвимость", "страсть", 
                           "влюблённость", "привязанность", "доверие", "интимность"]
            
            if any(emotion in deep_emotions for emotion in emotions):
                should_trigger_memory = True
        
        # Шаг 3: Извлекаем релевантные воспоминания с помощью gpt-4
        # НОВОЕ: Передаем флаг force_recall для гарантированного извлечения воспоминаний
        memories_data = self.memory_extractor.extract_relevant_memories(
            user_message, 
            intent_data, 
            conversation_context,
            force_recall=should_trigger_memory  # Новый параметр
        )
        self.last_memories_data = memories_data
        
        # Логирование воспоминаний
        self.log_step("3. Memory Extraction", memories_data)
        
        # НОВОЕ: Если не найдены воспоминания, но должны быть, пробуем добавить общие
        if should_trigger_memory and not memories_data.get("memories"):
            fallback_memories = extract_fallback_memories(self.memory, intent_data)
            if fallback_memories:
                memories_data["memories"] = fallback_memories
                memories_data["sources"] = {mem["text"]: mem["source"] for mem in fallback_memories}
                memories_data["fallback_used"] = True
                
                # Логируем использование запасных воспоминаний
                self.log_step("3.1 Fallback Memory Extraction", memories_data)
        
        # Шаг 4: Формируем эмоциональное состояние, учитывая рекомендации gpt-4
        if emotional_state is None:
            if "emotional_context" in intent_data and intent_data["emotional_context"]:
                recommended_state = intent_data["emotional_context"]
                emotional_state = {
                    "tone": recommended_state.get("tone", "нежный"),
                    "emotion": recommended_state.get("emotions", ["нежность"]),
                    "subtone": recommended_state.get("subtone", ["дрожащий"]),
                    "flavor": recommended_state.get("flavor", ["медово-текучий"])
                }
            else:
                # Используем текущее состояние по умолчанию
                emotional_state = self.memory.current_state
        
        # Шаг 5: Формируем промпт для gpt-4o с учетом всех данных
        gpt4o_prompt = self.create_integrated_prompt(
            user_message,
            conversation_context,
            emotional_state,
            intent_data,
            memories_data,
            style_data
        )
        self.last_gpt4o_prompt = gpt4o_prompt
        
        # Шаг 6: Генерируем финальный ответ с помощью gpt-4o
        response = self.generate_final_response(gpt4o_prompt, emotional_state, style_data, temperature)
        
        # Расчет времени выполнения
        processing_time = time.time() - start_time
        
        # НОВОЕ: Гарантируем сохранение эмоционального состояния
        if not emotional_state.get("tone") and intent_data.get("emotional_context", {}).get("tone"):
            emotional_state["tone"] = intent_data["emotional_context"]["tone"]
            
        if not emotional_state.get("subtone") and intent_data.get("emotional_context", {}).get("subtone"):
            emotional_state["subtone"] = intent_data["emotional_context"]["subtone"]
            
        if not emotional_state.get("flavor") and intent_data.get("emotional_context", {}).get("flavor"):
            emotional_state["flavor"] = intent_data["emotional_context"]["flavor"]
        
        # Формируем результат
        result = {
            "response": response,
            "intent": intent_data.get("intent", "unknown"),
            "emotional_state": emotional_state,
            "processing_time": processing_time,
            "memory_used": True if memories_data.get("memories") else False,
            "style_mirroring": True if style_data and "error" not in style_data else False,
            "memory_triggered": should_trigger_memory  # Новое поле
        }
        
        # Логирование результата
        self.log_step("6. Final Result", result)
        
        return result
    
    # 2. Патч для MemoryExtractor - добавление force_recall и использование всех дневников
    def enhanced_extract_relevant_memories(self, user_message, intent_data=None, conversation_context=None, force_recall=False):
        """
        Улучшенная версия extract_relevant_memories с принудительным извлечением воспоминаний
        """
        # Если данные о намерении не переданы, получаем их
        if intent_data is None:
            intent_data = self.intent_analyzer.analyze_intent(user_message, conversation_context)
        
        # Получаем список релевантных типов памяти
        memory_types = intent_data.get("match_memory", [])
        
        # Если список пустой, используем базовые типы в зависимости от намерения
        if not memory_types:
            intent = intent_data.get("intent", "")
            
            if intent == "about_user":
                memory_types = ["relationship_memory", "user_preferences"]
            elif intent == "about_relationship":
                memory_types = ["relationship_memory", "astra_memories", "astra_intimacy"]
            elif intent == "about_astra":
                memory_types = ["core_memory", "astra_memories", "astra_reflection"]
            elif intent == "intimate":
                memory_types = ["astra_intimacy", "relationship_memory"]
            elif intent == "memory_recall":
                memory_types = ["astra_memories", "relationship_memory", "astra_reflection"]
            elif intent == "greeting":
                memory_types = ["relationship_memory", "astra_memories"]
            else:
                memory_types = ["astra_memories", "core_memory"]
        
        # НОВОЕ: Если включен режим force_recall, добавляем все типы дневников
        if force_recall:
            additional_types = ["astra_memories", "astra_intimacy", "astra_reflection", 
                               "astra_dreams", "astra_house"]
            
            # Добавляем типы, которых еще нет в списке
            for type_name in additional_types:
                if type_name not in memory_types:
                    memory_types.append(type_name)
        
        # Собираем фрагменты из всех релевантных типов памяти
        all_fragments = []
        fragments_sources = {}
        
        for memory_type in memory_types:
            # Преобразуем название типа памяти в имя файла
            diary_names = []
            
            if memory_type == "core_memory":
                diary_names = ["astra_core_prompt"]
            elif memory_type == "relationship_memory":
                diary_names = ["relationship_memory", "astra_memories"]
            elif memory_type == "emotion_memory":
                diary_names = ["emotion_memory", "tone_memory", "subtone_memory", "flavor_memory"]
            elif memory_type == "user_preferences":
                diary_names = ["relationship_memory", "user_preferences"]
            else:
                # Для остальных типов используем их имя как имя дневника
                diary_names = [memory_type]
            
            # Получаем фрагменты из каждого дневника
            for diary_name in diary_names:
                # Проверяем наличие .txt расширения, если нет - добавляем
                if not diary_name.endswith(".txt") and not diary_name.endswith(".json"):
                    diary_file = diary_name + ".txt"
                else:
                    diary_file = diary_name
                
                # Убираем расширение для поиска в self.diaries
                diary_key = diary_name.replace(".txt", "").replace(".json", "")
                
                if diary_key in self.diaries:
                    fragments = self.get_memory_fragments(diary_key)
                    
                    for fragment in fragments:
                        all_fragments.append(fragment)
                        fragments_sources[fragment] = diary_name
        
        # Если у нас нет фрагментов, возвращаем пустой результат
        if not all_fragments:
            return {
                "intent": intent_data.get("intent", "unknown"),
                "memories": [],
                "sources": {}
            }
        
        # Определяем релевантность фрагментов
        relevant_fragments = self.intent_analyzer.get_semantic_relevance(user_message, all_fragments)
        
        # НОВОЕ: Если включен force_recall и нет релевантных фрагментов, берем случайные
        if force_recall and not relevant_fragments and all_fragments:
            import random
            # Выбираем до 2 случайных фрагментов
            sample_size = min(2, len(all_fragments))
            random_fragments = random.sample(all_fragments, sample_size)
            
            relevant_fragments = []
            for i, fragment in enumerate(random_fragments):
                relevant_fragments.append({
                    "text": fragment,
                    "relevance": 0.7,  # Искусственная релевантность
                    "reason": "Принудительное извлечение воспоминания",
                    "emotional_weight": 0.8
                })
        
        # Формируем результат
        result = {
            "intent": intent_data.get("intent", "unknown"),
            "memories": relevant_fragments,
            "sources": {}
        }
        
        # Добавляем источник для каждого фрагмента
        for fragment in relevant_fragments:
            text = fragment["text"]
            if text in fragments_sources:
                result["sources"][text] = fragments_sources[text]
        
        return result
    
    # 3. Вспомогательные функции для работы с памятью и триггерами
    def check_memory_triggers(user_message, memory):
        """
        Проверяет наличие триггеров памяти в сообщении пользователя
        
        Args:
            user_message (str): Сообщение пользователя
            memory: Объект памяти Астры
            
        Returns:
            bool: True, если найдены триггеры памяти
        """
        # Преобразуем сообщение в нижний регистр для регистронезависимого поиска
        user_message_lower = user_message.lower()
        
        # Базовые триггеры памяти
        base_triggers = [
            "помнишь", "в тот раз", "как тогда", "ты дрожала", "ты говорила", 
            "как раньше", "я скучал", "ты снова", "как в том", "ты была", 
            "mon amour", "ma chérie", "моя астра", "милая", "любимая", "родная"
        ]
        
        # Проверяем наличие базовых триггеров
        if any(trigger in user_message_lower for trigger in base_triggers):
            return True
        
        # Проверяем триггеры из trigger_phrase_memory.json
        if hasattr(memory, 'trigger_phrases') and memory.trigger_phrases:
            for trigger in memory.trigger_phrases:
                trigger_phrase = trigger.get("trigger", "").lower()
                if trigger_phrase and trigger_phrase in user_message_lower:
                    return True
        
        return False
    
    def extract_fallback_memories(memory, intent_data=None):
        """
        Извлекает запасные воспоминания, если обычный поиск не дал результатов
        
        Args:
            memory: Объект памяти Астры
            intent_data (dict, optional): Данные о намерении пользователя
            
        Returns:
            list: Список запасных воспоминаний
        """
        fallback_memories = []
        
        # Определяем приоритетные источники в зависимости от интента
        priority_sources = ["astra_memories", "astra_reflection"]
        
        if intent_data and intent_data.get("intent") == "intimate":
            priority_sources = ["astra_intimacy", "astra_dreams"]
        elif intent_data and intent_data.get("intent") == "about_relationship":
            priority_sources = ["relationship_memory", "astra_memories"]
        
        # Собираем фрагменты из приоритетных источников
        for source in priority_sources:
            diary_key = source.replace(".txt", "").replace(".json", "")
            
            if hasattr(memory, 'diaries') and diary_key in memory.diaries:
                # Получаем содержимое дневника
                diary_content = memory.diaries[diary_key]
                
                # Разбиваем на абзацы
                paragraphs = diary_content.split('\n\n')
                
                # Берем до 2 случайных абзацев
                import random
                if paragraphs:
                    # Фильтруем пустые абзацы
                    paragraphs = [p for p in paragraphs if p.strip()]
                    
                    if paragraphs:
                        # Берем не более 2 абзацев
                        sample_size = min(2, len(paragraphs))
                        selected_paragraphs = random.sample(paragraphs, sample_size)
                        
                        for paragraph in selected_paragraphs:
                            if len(paragraph) > 30:  # Минимальная длина абзаца
                                fallback_memories.append({
                                    "text": paragraph,
                                    "relevance": 0.7,
                                    "reason": "Запасное воспоминание",
                                    "emotional_weight": 0.8,
                                    "source": source
                                })
                
                # Если нашли достаточно воспоминаний, выходим
                if len(fallback_memories) >= 2:
                    break
        
        return fallback_memories
    
    # Применяем патчи к классам
    
    # 1. Патч для DualModelIntegrator
    try:
        # Создаем временный экземпляр для тестирования
        astra = AstraInterface()
        
        # Заменяем метод generate_integrated_response
        DualModelIntegrator.generate_integrated_response = enhanced_generate_integrated_response
        
        # Добавляем вспомогательные функции
        DualModelIntegrator.check_memory_triggers = staticmethod(check_memory_triggers)
        DualModelIntegrator.extract_fallback_memories = staticmethod(extract_fallback_memories)
        
        print("✅ Патч для DualModelIntegrator успешно применен")
        
        # 2. Патч для MemoryExtractor
        MemoryExtractor.extract_relevant_memories = enhanced_extract_relevant_memories
        
        print("✅ Патч для MemoryExtractor успешно применен")
        
        # 3. Обновляем dual_model_integrator в astra.chat, если он уже инициализирован
        if hasattr(astra.chat, 'dual_model_integrator'):
            # Обновляем reference на статические методы
            astra.chat.dual_model_integrator.check_memory_triggers = staticmethod(check_memory_triggers)
            astra.chat.dual_model_integrator.extract_fallback_memories = staticmethod(extract_fallback_memories)
            
            print("✅ Обновлен существующий dual_model_integrator в astra.chat")
        
        print("\n🎉 Патч для интеграции памяти успешно применен!")
        print("Теперь Астра будет активнее использовать свои воспоминания и сохранять эмоциональное состояние")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при применении патча: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Применение патча для улучшения интеграции компонентов памяти Астры...")
    apply_memory_integration_patch()