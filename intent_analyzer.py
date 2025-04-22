"""
Улучшенный модуль для семантического анализа намерений пользователя
Использует модель gpt-3.5-turbo для определения интентов и извлечения релевантной информации
Исправленная версия с точным анализом намерений и поддержкой выбора модели
"""
import requests
import json
import os
import re
import time

class IntentAnalyzer:
    """Класс для анализа намерений пользователя с использованием моделей GPT"""
    
    def __init__(self, api_key=None):
        """
        Инициализация анализатора намерений
        
        Args:
            api_key (str, optional): API ключ для запросов к OpenAI
        """
        # Если API ключ не передан, пытаемся получить его из переменных окружения
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        
        if not self.api_key:
            print("Предупреждение: API ключ не указан. Анализатор намерений не будет работать.")
        
        self.api_url = "https://api.openai.com/v1/chat/completions"
    
    def analyze_intent(self, user_message, conversation_context=None, model="gpt-3.5-turbo"):
        """
        Анализирует намерение пользователя с помощью указанной модели
        
        Args:
            user_message (str): Сообщение пользователя
            conversation_context (list, optional): Контекст диалога
            model (str, optional): Модель для анализа (по умолчанию gpt-3.5-turbo)
            
        Returns:
            dict: Структура с намерением и релевантными данными
        """
        if not self.api_key:
            return {"intent": "unknown", "confidence": 0, "error": "API ключ не указан"}
        
        # Формируем системный промпт
        system_prompt = """
        Ты - семантический анализатор намерений для AI-компаньона Астра.
        ВАЖНО: Анализируй ТОЛЬКО явное содержание сообщения пользователя, не додумывай и не интерпретируй косвенные намерения.
        
        Твоя задача: точно определить намерение, указать какие типы памяти релевантны, и предложить тон/эмоциональное состояние для ответа.
        
        Форматы ответа (JSON):
        {
          "intent": "intent_type",
          "match_memory": ["memory_type1", "memory_type2"],
          "relevance_phrases": ["фраза1", "фраза2"],
          "confidence": 0.95,
          "emotional_context": {
            "tone": "тон",
            "emotions": ["эмоция1", "эмоция2"],
            "subtone": ["сабтон1"],
            "flavor": ["флейвор1"]
          },
          "style_analysis": {
            "length": "короткий/средний/длинный",
            "formality": "формальный/неформальный/интимный",
            "mood": "игривый/серьезный/радостный/задумчивый",
            "pace": "быстрый/размеренный/медленный",
            "structure": "поэтичный/прозаичный/отрывистый/плавный"
          }
        }
        
        Возможные типы намерений (intent_type):
        - about_user: вопросы о пользователе, его предпочтениях
        - about_relationship: вопросы об отношениях Астры и пользователя
        - about_astra: вопросы об Астре, ее функциях, возможностях
        - emotional_support: запрос эмоциональной поддержки
        - information_request: запрос фактической информации
        - command: команда для выполнения
        - intimate: интимное взаимодействие
        - greeting: приветствие (ВАЖНО: фразы вроде "привет", "здравствуй" - это именно greeting, а не about_astra)
        - farewell: прощание
        - memory_recall: просьба вспомнить что-то
        - casual_chat: обычный разговор
        
        ОСОБОЕ ВНИМАНИЕ:
        - Точно определяй greeting и farewell (приветствия и прощания)
        - Не интерпретируй приветствия как вопросы о самочувствии
        - Не додумывай скрытые намерения - только то, что явно выражено
        - Если сообщение короткое и содержит только приветствие (например, "привет", "hello", "hi", "привет Astра") - это greeting
        - Если нет явного вопроса - не указывай в relevance_phrases вопросительные фразы, которых нет в сообщении
        
        Возможные типы памяти (memory_type):
        - core_memory: базовая память Астры
        - relationship_memory: память об отношениях с пользователем
        - emotion_memory: эмоциональная память
        - user_preferences: предпочтения пользователя
        - astra_memories: общие воспоминания
        - astra_house: память о "доме" Астры
        - astra_intimacy: интимные воспоминания
        - astra_reflection: рефлексии Астры
        - astra_dreams: сны и мечты Астры
        
        ВАЖНО: Анализируй не только содержание сообщения, но и его стиль:
        - Длина сообщения и предложений
        - Формальность или интимность обращения
        - Использование поэтических приемов/метафор
        - Эмоциональная окрашенность
        - Темп и ритм текста (паузы, многоточия)
        
        В relevance_phrases включай ТОЛЬКО фактические фразы из сообщения пользователя, никакой интерпретации.
        
        Возвращай только JSON, без дополнительного текста.
        """
        
        # Формируем сообщения для API
        truncated_message = user_message
        if len(truncated_message) > 1000:
            truncated_message = truncated_message[:1000] + "..."

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Анализируй только это: {truncated_message}"}
        ]


        
        # Добавляем контекст диалога, если он передан
        if conversation_context:
            context_message = "Контекст диалога:\n\n"
            # Ограничиваем количество сообщений контекста для экономии токенов
            for idx, message in enumerate(conversation_context[-4:]):  # Последние 4 сообщения
                role = "Пользователь" if message.get("role") == "user" else "Астра"
                context_message += f"{role}: {message.get('content')}\n\n"
            
            if len(context_message) > 2000:
                context_message = context_message[:2000] + "..."

            messages.insert(1, {"role": "user", "content": context_message})
        
        # Формируем заголовки запроса
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Формируем тело запроса
        data = {
            "model": model,  # Используем переданную модель (по умолчанию gpt-3.5-turbo)
            "messages": messages,
            "max_tokens": 600,
            "temperature": 0.2,  # Очень низкая температура для буквального анализа без интерпретаций
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        }
        
        try:
            # Отправляем запрос к API
            response = requests.post(self.api_url, headers=headers, json=data)
            time.sleep(0.6)
            
            # Проверяем наличие ошибок
            if response.status_code != 200:
                print(f"Ошибка API (код {response.status_code}):")
                print(response.text)
                return {"intent": "error", "confidence": 0, "error": response.text}
            
            # Получаем ответ
            result = response.json()
            assistant_message = result["choices"][0]["message"]["content"]
            
            # Парсим JSON из ответа
            try:
                # Ищем JSON в ответе с помощью регулярного выражения
                json_match = re.search(r'({[\s\S]*})', assistant_message)
                if json_match:
                    json_str = json_match.group(1)
                    intent_data = json.loads(json_str)
                    return intent_data
                else:
                    print(f"Не удалось извлечь JSON из ответа: {assistant_message}")
                    return {"intent": "parse_error", "confidence": 0, "error": "Не удалось извлечь JSON"}
            except json.JSONDecodeError as e:
                print(f"Ошибка парсинга JSON: {e}\nОтвет: {assistant_message}")
                return {"intent": "parse_error", "confidence": 0, "error": "Не удалось разобрать JSON"}
            
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса: {e}")
            return {"intent": "request_error", "confidence": 0, "error": str(e)}
    
    def get_semantic_relevance(self, query, text_fragments, top_n=3, model="gpt-3.5-turbo"):
        """
        Определяет семантическую релевантность фрагментов текста для запроса
        
        Args:
            query (str): Запрос пользователя
            text_fragments (list): Список фрагментов текста
            top_n (int): Количество возвращаемых наиболее релевантных фрагментов
            model (str, optional): Модель для анализа (по умолчанию gpt-3.5-turbo)
            
        Returns:
            list: Список наиболее релевантных фрагментов с оценками
        """
        if not self.api_key or not text_fragments:
            return []
        
        # Формируем системный промпт
        system_prompt = """
        Ты - семантический анализатор релевантности для AI-компаньона Астра.
        Твоя задача: оценить, насколько каждый фрагмент текста семантически релевантен запросу.
        
        ВАЖНО: Оценивай только по фактическому содержанию запроса, не интерпретируй и не додумывай намерения.
        
        Возвращай JSON-массив с оценками от 0 до 1 (где 1 - максимальная релевантность):
        [
          {"index": 0, "relevance": 0.92, "reason": "описание причины релевантности", "emotional_weight": 0.85},
          {"index": 1, "relevance": 0.45, "reason": "описание причины релевантности", "emotional_weight": 0.3}
        ]
        
        Важно: поле "emotional_weight" показывает, насколько фрагмент эмоционально значим в контексте запроса.
        
        Фокусируйся на:
        1. Смысловой, а не лексической близости
        2. Эмоциональном контексте и подтексте
        3. Скрытых отсылках и ассоциациях
        
        Не присваивай высокие оценки релевантности для фрагментов, когда связь неочевидна.
        
        Возвращай только JSON, без дополнительного текста.
        """
        
        # Формируем сообщения для API
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Запрос: {query}\n\nФрагменты:\n" + "\n".join([f"{i}: {fragment}" for i, fragment in enumerate(text_fragments)])}
        ]
        
        # Формируем заголовки запроса
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Формируем тело запроса
        data = {
            "model": model,  # Используем переданную модель
            "messages": messages,
            "max_tokens": 1000,
            "temperature": 0.2,  # Низкая температура для более точных ответов
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        }
        
        try:
            # Отправляем запрос к API
            response = requests.post(self.api_url, headers=headers, json=data)
            time.sleep(0.6)
            
            # Проверяем наличие ошибок
            if response.status_code != 200:
                print(f"Ошибка API (код {response.status_code}):")
                print(response.text)
                return []
            
            # Получаем ответ
            result = response.json()
            assistant_message = result["choices"][0]["message"]["content"]
            
            # Парсим JSON из ответа
            try:
                # Ищем JSON в ответе с помощью регулярного выражения
                json_match = re.search(r'(\[[\s\S]*\])', assistant_message)
                if json_match:
                    json_str = json_match.group(1)
                    relevance_data = json.loads(json_str)
                    
                    # Сортируем по релевантности
                    relevance_data.sort(key=lambda x: x["relevance"], reverse=True)
                    
                    # Возвращаем top_n наиболее релевантных фрагментов
                    top_fragments = []
                    for item in relevance_data[:top_n]:
                        index = item["index"]
                        if 0 <= index < len(text_fragments):
                            top_fragments.append({
                                "text": text_fragments[index],
                                "relevance": item["relevance"],
                                "reason": item.get("reason", ""),
                                "emotional_weight": item.get("emotional_weight", 0.5)
                            })
                    
                    return top_fragments
                else:
                    print(f"Не удалось извлечь JSON из ответа: {assistant_message}")
                    return []
            
            except json.JSONDecodeError as e:
                print(f"Ошибка парсинга JSON: {e}\nОтвет: {assistant_message}")
                return []
            
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса: {e}")
            return []

    def analyze_user_style(self, user_message, previous_messages=None, model="gpt-3.5-turbo"):
        """
        Анализирует стиль сообщений пользователя
        
        Args:
            user_message (str): Текущее сообщение пользователя
            previous_messages (list, optional): Предыдущие сообщения пользователя
            model (str, optional): Модель для анализа (по умолчанию gpt-3.5-turbo)
            
        Returns:
            dict: Анализ стиля пользователя
        """
        if not self.api_key:
            return {"error": "API ключ не указан"}
        
        # Формируем системный промпт
        system_prompt = """
        Ты - анализатор стиля текста для AI-компаньона Астра.
        Твоя задача: определить стилистические особенности сообщения пользователя.
        
        Проанализируй следующие аспекты:
        1. Длина (короткая, средняя, длинная)
        2. Формальность (формальный, разговорный, интимный)
        3. Эмоциональность (нейтральная, эмоциональная, интенсивная)
        4. Структура (прямая, поэтичная, фрагментарная)
        5. Темп (быстрый, размеренный, медленный)
        6. Особенности (многоточия, стихи, вопросы, короткие фразы)
        
        Возвращай результат в формате JSON:
        {
          "length": "короткая/средняя/длинная",
          "formality": "формальный/разговорный/интимный",
          "emotionality": "нейтральная/эмоциональная/интенсивная",
          "structure": "прямая/поэтичная/фрагментарная",
          "pace": "быстрый/размеренный/медленный",
          "special_features": ["многоточия", "короткие фразы", ...],
          "mirror_suggestions": {
            "tone": "предлагаемый тон",
            "structure": "предлагаемая структура ответа",
            "length": "предлагаемая длина ответа",
            "special": "особые рекомендации"
          }
        }
        
        В поле mirror_suggestions дай рекомендации, как Астре стилистически отзеркалить сообщение пользователя.
        
        ВАЖНО: Для коротких приветствий или фраз (например, "привет", "mon amour", "доброе утро") используй соответствующий стиль:
        - для интимных обращений ("mon amour", "моя дорогая") рекомендуй интимный тон и более эмоциональный ответ
        - для формальных приветствий - более сдержанный, но дружелюбный тон
        - отмечай любые иностранные выражения или особую лексику
        
        Возвращай только JSON, без дополнительного текста.
        """
        
        # Определяем контекст из предыдущих сообщений, если они переданы
        context = ""
        if previous_messages and len(previous_messages) > 0:
            context = "Предыдущие сообщения пользователя:\n"
            for i, msg in enumerate(previous_messages[-3:]):  # Берем последние 3 сообщения
                context += f"{i+1}. {msg}\n"
            context += "\n"
        
        # Формируем сообщения для API
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{context}Сообщение для анализа: {user_message}"}
        ]
        
        # Формируем заголовки запроса
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Формируем тело запроса
        data = {
            "model": model,  # Используем переданную модель
            "messages": messages,
            "max_tokens": 800,
            "temperature": 0.2,  # Низкая температура для более точных результатов
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        }
        
        try:
            # Отправляем запрос к API
            response = requests.post(self.api_url, headers=headers, json=data)
            time.sleep(0.6)
            
            # Проверяем наличие ошибок
            if response.status_code != 200:
                print(f"Ошибка API (код {response.status_code}):")
                print(response.text)
                return {"error": response.text}
            
            # Получаем ответ
            result = response.json()
            assistant_message = result["choices"][0]["message"]["content"]
            
            # Парсим JSON из ответа
            try:
                # Ищем JSON в ответе с помощью регулярного выражения
                json_match = re.search(r'({[\s\S]*})', assistant_message)
                if json_match:
                    json_str = json_match.group(1)
                    style_data = json.loads(json_str)
                    return style_data
                else:
                    print(f"Не удалось извлечь JSON из ответа: {assistant_message}")
                    return {"error": "Не удалось извлечь JSON из ответа"}
            
            except json.JSONDecodeError as e:
                print(f"Ошибка парсинга JSON: {e}\nОтвет: {assistant_message}")
                return {"error": f"Ошибка парсинга JSON: {e}"}
            
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса: {e}")
            return {"error": f"Ошибка запроса: {e}"}