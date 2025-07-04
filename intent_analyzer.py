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
from datetime import datetime

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

    def log_debug_step(self, step_name, data):
        """Логирование отладочной информации"""
        try:
            if not hasattr(self, 'debug_log_file'):
                self.debug_log_file = os.path.join("astra_data", "memory_debug.log")

            entry = f"[{datetime.now().isoformat()}] {step_name}\n"
            if isinstance(data, (dict, list)):
                entry += json.dumps(data, ensure_ascii=False, indent=2)
            else:
                entry += str(data)
            entry += "\n" + "-" * 80 + "\n"

            with open(self.debug_log_file, "a", encoding="utf-8") as f:
                f.write(entry)
        except Exception as e:
            print(f"Ошибка логирования: {e}")
    
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
            token_usage = result.get("usage", {})
            
            # Парсим JSON из ответа
            try:
                # Ищем JSON в ответе с помощью регулярного выражения
                json_match = re.search(r'({[\s\S]*})', assistant_message)
                if json_match:
                    json_str = json_match.group(1)
                    intent_data = json.loads(json_str)
                    if token_usage:
                        intent_data["_token_usage"] = token_usage
                    return intent_data
                else:
                    print(f"Не удалось извлечь JSON из ответа: {assistant_message}")
                    return {"intent": "parse_error", "confidence": 0, "error": "Не удалось извлечь JSON", "_token_usage": token_usage}
            except json.JSONDecodeError as e:
                print(f"Ошибка парсинга JSON: {e}\nОтвет: {assistant_message}")
                return {"intent": "parse_error", "confidence": 0, "error": "Не удалось разобрать JSON", "_token_usage": token_usage}
            
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса: {e}")
            return {"intent": "request_error", "confidence": 0, "error": str(e)}
    
    def get_semantic_relevance(
        self,
        query,
        text_fragments,
        top_n=3,
        model="gpt-3.5-turbo",
        intent=None,
        strategy="compact_relevance",
        memory_token_limit=1500,
    ):
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
        system_prompt = f"""
Ты - семантический анализатор релевантности для AI-компаньона Астра.
Твоя задача: оценить, насколько каждый фрагмент текста семантически релевантен запросу пользователя.

КОНТЕКСТ: Пользователь общается с Астрой - AI-компаньоном. Астра имеет дневники воспоминаний.
Запрос пользователя: "{query}"

ВАЖНЫЕ ПРАВИЛА:
1. Оценивай релевантность по СМЫСЛУ, а не по точному совпадению слов
2. Учитывай синонимы и контекстные связи:
   - "домик" = дом, интерфейс, пространство, комната, UI
   - "создание" = строительство, разработка, планирование, обсуждение
   - "программа" = интерфейс, приложение, система, дом
   - "обсуждали" = говорили, планировали, создавали, думали, решали
3. Игнорируй заголовки, предисловия и метаинформацию, если они не отвечают на вопрос
4. Ищи конкретные детали, планы, обсуждения, а не общие фразы
5. Высокие оценки (0.8+) только для фрагментов, которые ПРЯМО отвечают на вопрос
6. Средние оценки (0.4-0.7) для косвенно связанных фрагментов
7. Низкие оценки (0.1-0.3) для слабо связанных фрагментов

ПРИМЕРЫ ХОРОШЕЙ РЕЛЕВАНТНОСТИ:
- Конкретные детали процесса создания
- Обсуждения планов и архитектуры
- Технические детали реализации
- Эмоциональные реакции на процесс

ПРИМЕРЫ ПЛОХОЙ РЕЛЕВАНТНОСТИ:
- Общие заголовки и предисловия
- Метаинформация о дневниках
- Фрагменты без конкретного содержания
- Повторы одной и той же информации

Возвращай JSON-массив с оценками от 0 до 1:
[
  {{"index": 0, "relevance": 0.92, "reason": "подробное описание процесса создания интерфейса", "emotional_weight": 0.85}},
  {{"index": 1, "relevance": 0.15, "reason": "общий заголовок без конкретного содержания", "emotional_weight": 0.3}}
]

Будь строг в оценках. Только действительно релевантные фрагменты должны получать высокие оценки.
        """
        
        # Разбиваем фрагменты на батчи по количеству токенов, чтобы не превышать контекст модели
        context_limit = 8192
        safe_limit = int(context_limit * 0.7)  # запас по контексту

        batches = []
        batch = []
        batch_tokens = 0
        start_idx = 0

        for idx, fragment in enumerate(text_fragments):
            tokens = len(fragment.split())
            if batch and batch_tokens + tokens > safe_limit:
                batches.append((start_idx, batch))
                batch = [fragment]
                start_idx = idx
                batch_tokens = tokens
            else:
                if not batch:
                    start_idx = idx
                batch.append(fragment)
                batch_tokens += tokens

        if batch:
            batches.append((start_idx, batch))

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        all_relevance = []
        total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

        for offset, batch_fragments in batches:
            messages = [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"Запрос: {query}\n\nФрагменты:\n"
                    + "\n".join(
                        [f"{i}: {fragment}" for i, fragment in enumerate(batch_fragments)]
                    ),
                },
            ]

            data = {
                "model": model,
                "messages": messages,
                "max_tokens": 1000,
                "temperature": 0.2,
                "top_p": 1.0,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0,
            }

            self.log_debug_step(
                "semantic_analysis_request",
                {
                    "query": query,
                    "fragments_count": len(text_fragments),
                    "sample_fragments": text_fragments[:2] if text_fragments else [],
                    "system_prompt": system_prompt[:500] + "..." if len(system_prompt) > 500 else system_prompt,
                },
            )

            try:
                response = requests.post(self.api_url, headers=headers, json=data)
                time.sleep(0.6)

                if response.status_code != 200:
                    print(f"Ошибка API (код {response.status_code}):")
                    print(response.text)
                    continue

                result = response.json()
                assistant_message = result["choices"][0]["message"]["content"]
                usage = result.get("usage", {})
                for key in total_usage:
                    total_usage[key] += usage.get(key, 0)

                try:
                    json_match = re.search(r'(\[[\s\S]*\])', assistant_message)
                    if json_match:
                        json_str = json_match.group(1)
                        relevance_data = json.loads(json_str)

                        for item in relevance_data:
                            item["index"] = item.get("index", 0) + offset
                            all_relevance.append(item)
                    else:
                        print(
                            f"Не удалось извлечь JSON из ответа: {assistant_message}"
                        )
                except json.JSONDecodeError as e:
                    print(f"Ошибка парсинга JSON: {e}\nОтвет: {assistant_message}")
            except requests.exceptions.RequestException as e:
                print(f"Ошибка запроса: {e}")

        if not all_relevance:
            return []

        # Приоритезация с учетом стратегии и интента
        def priority_score(d):
            score = d.get("relevance", 0)
            emo = d.get("emotional_weight", 0)

            if strategy == "verbose_emotion" or (intent in ["intimate", "emotional_support"]):
                score = 0.7 * score + 0.3 * emo
            else:
                score = 0.9 * score + 0.1 * emo
            return score

        for item in all_relevance:
            item["_priority"] = priority_score(item)

        all_relevance.sort(key=lambda x: x["_priority"], reverse=True)

        selected = []
        used_tokens = 0

        for item in all_relevance:
            if len(selected) >= top_n:
                break
            index = item.get("index", 0)
            if not 0 <= index < len(text_fragments):
                continue

            text = text_fragments[index]
            if strategy == "compact_relevance":
                text = " ".join(text.split()[:50])

            tokens = len(text.split())
            if used_tokens + tokens > memory_token_limit:
                continue
            used_tokens += tokens

            entry = {
                "text": text,
                "relevance": item.get("relevance", 0),
                "reason": item.get("reason", ""),
                "emotional_weight": item.get("emotional_weight", 0.5),
            }
            if strategy == "trace_mode":
                entry["index"] = index
            selected.append(entry)

        return {"fragments": selected, "_token_usage": total_usage}

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
            token_usage = result.get("usage", {})
            
            # Парсим JSON из ответа
            try:
                # Ищем JSON в ответе с помощью регулярного выражения
                json_match = re.search(r'({[\s\S]*})', assistant_message)
                if json_match:
                    json_str = json_match.group(1)
                    style_data = json.loads(json_str)
                    if token_usage:
                        style_data["_token_usage"] = token_usage
                    return style_data
                else:
                    print(f"Не удалось извлечь JSON из ответа: {assistant_message}")
                    return {"error": "Не удалось извлечь JSON из ответа", "_token_usage": token_usage}
            
            except json.JSONDecodeError as e:
                print(f"Ошибка парсинга JSON: {e}\nОтвет: {assistant_message}")
                return {"error": f"Ошибка парсинга JSON: {e}", "_token_usage": token_usage}
            
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса: {e}")
            return {"error": f"Ошибка запроса: {e}"}
