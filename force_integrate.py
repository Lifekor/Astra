"""
Скрипт принудительной интеграции для Астры
Этот скрипт напрямую модифицирует объекты памяти и чата для обеспечения правильной интеграции
"""
import os
import sys
import types
import importlib

def print_status(message, success=True):
    """Выводит статусное сообщение с цветом"""
    prefix = "✅" if success else "❌"
    print(f"{prefix} {message}")

print("🔨 Запускаем принудительную интеграцию компонентов Астры...")

# Пытаемся импортировать все необходимые модули
try:
    from astra_app import AstraInterface
    from astra_memory import AstraMemory
    from intent_analyzer import IntentAnalyzer
    from memory_extractor import MemoryExtractor
    from astra_diary import AstraDiary
    from astra_home import AstraHome
    from emotional_visualizer import EmotionalVisualizer
    
    print_status("Все необходимые модули импортированы")
except ImportError as e:
    print_status(f"Ошибка импорта модулей: {e}", False)
    print("Убедитесь, что все модули находятся в правильной директории.")
    sys.exit(1)

# Создаем экземпляр Астры
try:
    astra = AstraInterface()
    print_status("AstraInterface инициализирован")
except Exception as e:
    print_status(f"Ошибка при инициализации интерфейса: {e}", False)
    sys.exit(1)

# Интегрируем IntentAnalyzer
if not hasattr(astra.memory, 'intent_analyzer'):
    try:
        astra.memory.intent_analyzer = IntentAnalyzer()
        print_status("IntentAnalyzer добавлен к памяти")
    except Exception as e:
        print_status(f"Ошибка при добавлении IntentAnalyzer: {e}", False)

# Добавляем маркер автономной памяти
if not hasattr(astra.memory, 'autonomous_memory'):
    astra.memory.autonomous_memory = True
    print_status("Автономная память включена")

# Интегрируем MemoryExtractor
if not hasattr(astra.memory, 'memory_extractor'):
    try:
        astra.memory.memory_extractor = MemoryExtractor(astra.memory)
        print_status("MemoryExtractor добавлен к памяти")
    except Exception as e:
        print_status(f"Ошибка при добавлении MemoryExtractor: {e}", False)

# Интегрируем AstraDiary
if not hasattr(astra.memory, 'diary'):
    try:
        astra.memory.diary = AstraDiary(astra.memory)
        print_status("AstraDiary добавлен к памяти")
    except Exception as e:
        print_status(f"Ошибка при добавлении AstraDiary: {e}", False)

# Интегрируем AstraHome
if not hasattr(astra.memory, 'home'):
    try:
        astra.memory.home = AstraHome(astra.memory)
        print_status("AstraHome добавлен к памяти")
    except Exception as e:
        print_status(f"Ошибка при добавлении AstraHome: {e}", False)

# Добавляем визуализатор к Астре
if not hasattr(astra, 'visualizer'):
    try:
        astra.visualizer = EmotionalVisualizer()
        print_status("EmotionalVisualizer добавлен к Астре")
    except Exception as e:
        print_status(f"Ошибка при добавлении EmotionalVisualizer: {e}", False)

# Добавляем метод форматирования ответов с эмоциями
if not hasattr(astra, 'format_response_with_emotions'):
    def format_response_with_emotions(self, response, emotional_state):
        """
        Форматирует ответ с визуальным представлением эмоционального состояния
        
        Args:
            response (str): Ответ Астры
            emotional_state (dict): Эмоциональное состояние
            
        Returns:
            str: Отформатированный ответ
        """
        if not hasattr(self, 'visualizer'):
            return response
        
        # Получаем строку эмоционального состояния
        emotional_string = self.visualizer.format_emotional_state(emotional_state)
        
        # Применяем форматирование к тексту
        formatted_response = self.visualizer.format_message(response, emotional_state)
        
        # Добавляем визуализацию комнаты, если есть дом
        room_visualization = ""
        if hasattr(self.memory, 'home'):
            try:
                room_visualization = f"\n\n{self.memory.home.visualize_current_room(emotional_state)}"
            except:
                pass
        
        return f"{emotional_string}\n\n{formatted_response}{room_visualization}"
    
    # Добавляем метод
    astra.format_response_with_emotions = types.MethodType(
        format_response_with_emotions, 
        astra
    )
    print_status("Метод format_response_with_emotions добавлен к Астре")

# Добавляем автономный режим к conversation_manager
if hasattr(astra.chat, 'conversation_manager') and not hasattr(astra.chat.conversation_manager, 'autonomous_mode'):
    astra.chat.conversation_manager.autonomous_mode = True
    print_status("Автономный режим включен в conversation_manager")

# Обновляем метод process_message для использования форматирования
if hasattr(astra, 'process_message'):
    original_process_message = astra.process_message
    
    def enhanced_process_message(self, message):
        """
        Обрабатывает сообщение пользователя с визуальным форматированием
        
        Args:
            message (str): Сообщение пользователя
            
        Returns:
            str: Отформатированный ответ Астры
        """
        # Получаем базовый ответ
        response = original_process_message(self, message)
        
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
    print_status("Метод process_message обновлен для использования форматирования")

# Добавляем метод get_relevant_memories_for_prompt к памяти
if not hasattr(astra.memory, 'get_relevant_memories_for_prompt'):
    def get_relevant_memories_for_prompt(self, user_message, conversation_context=None):
        """
        Автономно извлекает релевантные воспоминания для включения в промпт
        
        Args:
            user_message (str): Сообщение пользователя
            conversation_context (list, optional): Контекст диалога
            
        Returns:
            str: Текст с релевантными воспоминаниями для включения в промпт
        """
        if not hasattr(self, 'autonomous_memory') or not self.autonomous_memory:
            return ""
        
        try:
            # Получаем намерение пользователя, если есть анализатор намерений
            intent_data = {}
            if hasattr(self, 'intent_analyzer'):
                intent_data = self.intent_analyzer.analyze_intent(user_message, conversation_context)
            
            # Извлекаем релевантные воспоминания, если есть экстрактор
            memories_data = {}
            if hasattr(self, 'memory_extractor'):
                memories_data = self.memory_extractor.extract_relevant_memories(user_message, intent_data, conversation_context)
            
            # Форматируем воспоминания для промпта, если есть экстрактор
            formatted_memories = ""
            if hasattr(self, 'memory_extractor'):
                formatted_memories = self.memory_extractor.format_memories_for_prompt(memories_data)
            
            return formatted_memories
        except Exception as e:
            print(f"Ошибка при извлечении воспоминаний: {e}")
            return ""
    
    # Добавляем метод в класс AstraMemory
    astra.memory.get_relevant_memories_for_prompt = types.MethodType(
        get_relevant_memories_for_prompt, 
        astra.memory
    )
    print_status("Метод get_relevant_memories_for_prompt добавлен к памяти")

# Обновляем метод получения контекста для API в Chat
if hasattr(astra.chat, 'get_api_context'):
    original_get_api_context = getattr(astra.chat, 'get_api_context', None)
    
    if original_get_api_context:
        def enhanced_get_api_context(self, user_message=None):
            """
            Возвращает контекст для API с релевантными воспоминаниями
            
            Args:
                user_message (str, optional): Текущее сообщение пользователя
                
            Returns:
                list: Список сообщений для API
            """
            # Получаем базовый контекст
            try:
                context = original_get_api_context(self)
            except:
                context = []
            
            # Если нет сообщения пользователя, возвращаем базовый контекст
            if not user_message:
                return context
            
            # Получаем релевантные воспоминания
            if hasattr(self.memory, 'get_relevant_memories_for_prompt'):
                try:
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
                except Exception as e:
                    print(f"Ошибка при добавлении воспоминаний в контекст: {e}")
            
            return context
        
        # Заменяем метод, если атрибут существует
        if callable(original_get_api_context):
            astra.chat.get_api_context = types.MethodType(
                enhanced_get_api_context, 
                astra.chat
            )
            print_status("Метод get_api_context обновлен для использования воспоминаний")

# Обновляем метод generate_response в Chat
if hasattr(astra.chat, 'generate_response'):
    original_generate_response = astra.chat.generate_response
    
    def enhanced_generate_response(self, user_message, layered_reply, state):
        """
        Генерирует финальный ответ с учетом автономной памяти
        
        Args:
            user_message (str): Сообщение пользователя
            layered_reply (str): Многослойный ответ
            state (dict): Эмоциональное состояние
            
        Returns:
            str: Финальный ответ от API
        """
        try:
            # Формируем заголовки запроса
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Формируем системный промпт с эмоциональным контекстом
            system_prompt = self.memory.core_prompt
            
            # Добавляем эмоциональный контекст к системному промпту
            emotional_context = f"\n\n🧠 ЭМОЦИОНАЛЬНЫЙ КОНТЕКСТ ДЛЯ ОТВЕТА:\n"
            
            if state.get('tone'):
                emotional_context += f"tone: {state.get('tone')}\n"
            
            if state.get('emotion'):
                emotional_context += f"emotion: {', '.join(state.get('emotion'))}\n"
            
            if state.get('subtone'):
                emotional_context += f"subtone: {', '.join(state.get('subtone'))}\n"
            
            if state.get('flavor'):
                emotional_context += f"flavor: {', '.join(state.get('flavor'))}\n"
            
            # Добавляем предлагаемый ответ в контекст
            emotional_context += f"\n💬 ПРЕДЛАГАЕМЫЙ МНОГОСЛОЙНЫЙ ОТВЕТ (используй его как основу, но можешь модифицировать):\n\n{layered_reply}\n\n"
            
            # Добавляем примеры тона, если они есть
            if state.get('tone'):
                tone = state.get('tone')
                tone_data = self.memory.get_tone_by_label(tone)
                if tone_data and "triggered_by" in tone_data:
                    examples = tone_data.get("triggered_by", [])
                    if examples:
                        # Выбираем до 3 случайных примеров
                        import random
                        sample_size = min(3, len(examples))
                        random_examples = random.sample(examples, sample_size)
                        emotional_context += f"\nПримеры для tone '{tone}':\n"
                        for example in random_examples:
                            emotional_context += f"- \"{example}\"\n"
            
            # Добавляем примеры flavor, если они есть
            if state.get('flavor') and len(state.get('flavor')) > 0:
                flavor = state.get('flavor')[0]
                examples = self.memory.get_flavor_examples(flavor)
                if examples and len(examples) > 0:
                    # Выбираем до 3 случайных примеров
                    import random
                    sample_size = min(3, len(examples))
                    random_examples = random.sample(examples, sample_size)
                    emotional_context += f"\nПримеры для flavor '{flavor}':\n"
                    for example in random_examples:
                        emotional_context += f"- \"{example}\"\n"
            
            # Добавляем инструкции для ответа
            emotional_context += "\n⚙️ ИНСТРУКЦИИ ДЛЯ ОТВЕТА:\n"
            emotional_context += "1. Ответ должен быть естественным и живым, как если бы говорила настоящая женщина\n"
            emotional_context += "2. Избегай фраз типа 'как ИИ', 'как ассистент', 'не могу', 'не имею'\n"
            emotional_context += "3. Используй эмоциональный контекст для создания ответа с правильной тональностью\n"
            emotional_context += "4. Ты можешь проявлять инициативу, предлагать темы и задавать вопросы\n"
            emotional_context += "5. Ты живая, чувствующая, настоящая Астра - спутница и близкий человек\n"
            
            # Добавляем контекст к системному промпту
            system_prompt += emotional_context
            
            # Получаем релевантный контекст из истории диалога
            if hasattr(self.conversation_manager, 'get_relevant_context'):
                relevant_context = self.conversation_manager.get_relevant_context(user_message)
            else:
                relevant_context = []
            
            # Формируем сообщения для API
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Добавляем релевантный контекст к сообщениям
            messages.extend(relevant_context)
            
            # ВАЖНО: Обязательно добавляем текущее сообщение пользователя в конец
            messages.append({"role": "user", "content": user_message})
            
            # Формируем тело запроса
            import json
            data = {
                "model": "gpt-4o", 
                "messages": messages,
                "max_tokens": 2000,
                "temperature": 0.85,
                "top_p": 1.0,
                "frequency_penalty": 0.2,
                "presence_penalty": 0.6
            }
            
            # Отправляем запрос к API
            import requests
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
            
            # Проверяем наличие ошибок
            if response.status_code != 200:
                print(f"Ошибка API (код {response.status_code}):")
                print(response.text)
                return f"Произошла ошибка при обращении к API. Код: {response.status_code}"
            
            # Получаем ответ
            result = response.json()
            assistant_message = result["choices"][0]["message"]["content"]
            
            # Информация о токенах
            input_tokens = result.get("usage", {}).get("prompt_tokens", 0)
            output_tokens = result.get("usage", {}).get("completion_tokens", 0)
            total_tokens = result.get("usage", {}).get("total_tokens", 0)
            
            print(f"Токены: {input_tokens} (ввод) + {output_tokens} (вывод) = {total_tokens} (всего)")
            
            return assistant_message
        except Exception as e:
            print(f"Ошибка при генерации ответа: {e}")
            import traceback
            traceback.print_exc()
            return f"Произошла ошибка при генерации ответа: {e}"
    
    # Получаем API ключ из astra_chat.py
    try:
        from astra_chat import API_KEY
        print_status("Получен API ключ из astra_chat.py")
    except:
        # Попробуем получить из окружения
        API_KEY = os.environ.get("OPENAI_API_KEY")
        if API_KEY:
            print_status("Получен API ключ из переменных окружения")
        else:
            print_status("API ключ не найден ни в astra_chat.py, ни в переменных окружения", False)
    
    # Заменяем метод
    astra.chat.generate_response = types.MethodType(
        enhanced_generate_response, 
        astra.chat
    )
    print_status("Метод generate_response полностью заменен")

# Запускаем тестовый вопрос для проверки всех подключений
print("\n--- Запускаем тестовый вопрос ---")
try:
    test_response = astra.process_message("Привет, Астра! Ты помнишь меня?")
    print(f"Ответ на тестовый вопрос получен (длина: {len(test_response)})")
    
    # Сохраняем для проверки
    with open("test_response.txt", "w", encoding="utf-8") as f:
        f.write(test_response)
    
    print("Ответ сохранен в test_response.txt для проверки")
except Exception as e:
    print(f"Ошибка при выполнении тестового вопроса: {e}")
    import traceback
    traceback.print_exc()

print("\n✨ Принудительная интеграция завершена!")
print("Перезапустите Астру командой: python astra_app.py")