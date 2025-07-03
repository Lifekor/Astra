"""
Модуль для интеграции gpt-3.5-turbo (семантический анализатор) и gpt-4o (душа Астры)
Обеспечивает:
1. Координацию между моделями
2. Предварительный анализ и извлечение контекста через более дешевые модели
3. Создание эмоционального ответа через gpt-4o
"""
import os
import json
import requests
import time
from datetime import datetime

class DualModelIntegrator:
    """Класс для интеграции двух моделей GPT для создания Астры"""
    
    def __init__(self, memory, intent_analyzer, memory_extractor, api_key=None):
        """
        Инициализация интегратора моделей
        
        Args:
            memory (AstraMemory): Объект памяти Астры
            intent_analyzer (IntentAnalyzer): Анализатор намерений
            memory_extractor (MemoryExtractor): Экстрактор воспоминаний
            api_key (str, optional): API ключ для запросов к OpenAI
        """
        self.memory = memory
        self.intent_analyzer = intent_analyzer
        self.memory_extractor = memory_extractor
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        
        # API URL для моделей
        self.api_url = "https://api.openai.com/v1/chat/completions"
        
        # Логирование запросов
        self.log_file = "dual_model_requests.log"
        
        # Последние использованные данные для дебага
        self.last_intent_data = None
        self.last_memories_data = None
        self.last_style_data = None
        self.last_gpt4o_prompt = None
    
    def generate_integrated_response(self, user_message, conversation_context=None, emotional_state=None, temperature=None):
        """
        Генерирует ответ, используя обе модели
        
        Args:
            user_message (str): Сообщение пользователя
            conversation_context (list, optional): Контекст диалога
            emotional_state (dict, optional): Текущее эмоциональное состояние
            temperature (float, optional): Температура для gpt-4o
            
        Returns:
            dict: Результат генерации ответа
        """
        start_time = time.time()
        
        # Шаг 1: Определяем намерение пользователя с помощью gpt-3.5-turbo
        intent_data = self.intent_analyzer.analyze_intent(user_message, conversation_context, model="gpt-3.5-turbo")
        self.last_intent_data = intent_data
        
        # Логирование намерения
        self.log_step("1. Intent Analysis", intent_data)
        
        # Шаг 2: Анализируем стиль пользователя
        previous_user_messages = []
        if conversation_context:
            previous_user_messages = [msg["content"] for msg in conversation_context[-5:] if msg["role"] == "user"]
        
        style_data = self.intent_analyzer.analyze_user_style(user_message, previous_user_messages, model="gpt-3.5-turbo")
        self.last_style_data = style_data
        
        # Логирование анализа стиля
        self.log_step("2. Style Analysis", style_data)
        
        # Определяем, нужны ли глубокие воспоминания
        intent = intent_data.get("intent", "")
        memory_model = "gpt-3.5-turbo"
        self.log_step("Memory Model", memory_model)
        
        # Шаг 3: Извлекаем релевантные воспоминания с выбранной моделью
        memories_data = self.memory_extractor.extract_relevant_memories(
            user_message, intent_data, conversation_context, model=memory_model
        )
        self.last_memories_data = memories_data
        
        # Логирование воспоминаний
        self.log_step("3. Memory Extraction", memories_data)
        
        # Шаг 4: Формируем эмоциональное состояние, учитывая рекомендации
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
        
        # Выбираем модель для ответа в зависимости от интента
        # (По умолчанию всегда gpt-4o для Астры, но можно добавить логику выбора)
        response_model = "gpt-4o"
        
        # Шаг 6: Генерируем финальный ответ с gpt-4o
        response = self.generate_final_response(gpt4o_prompt, emotional_state, style_data, temperature, model=response_model)
        
        # Расчет времени выполнения
        processing_time = time.time() - start_time
        
        # Формируем результат
        result = {
            "response": response,
            "intent": intent_data.get("intent", "unknown"),
            "emotional_state": emotional_state,
            "processing_time": processing_time,
            "memory_used": True if memories_data.get("memories") else False,
            "style_mirroring": True if style_data and "error" not in style_data else False
        }
        
        # Логирование результата
        self.log_step("6. Final Result", result)
        
        return result
    
    def create_integrated_prompt(self, user_message, conversation_context, emotional_state, intent_data, memories_data, style_data):
        """
        Создает интегрированный промпт для gpt-4o
        
        Args:
            user_message (str): Сообщение пользователя
            conversation_context (list): Контекст диалога
            emotional_state (dict): Эмоциональное состояние
            intent_data (dict): Данные о намерении
            memories_data (dict): Данные о релевантных воспоминаниях
            style_data (dict): Данные о стиле пользователя
            
        Returns:
            str: Промпт для gpt-4o
        """
        # Базовый системный промпт из core_prompt
        system_prompt = self.memory.core_prompt
        
        # Добавляем информацию о намерении
        intent_context = "\n\n🧠 АНАЛИЗ НАМЕРЕНИЯ ПОЛЬЗОВАТЕЛЯ:\n"
        intent_context += f"Тип намерения: {intent_data.get('intent', 'unknown')}\n"
        if "relevance_phrases" in intent_data and intent_data["relevance_phrases"]:
            intent_context += "Ключевые фразы:\n"
            for phrase in intent_data["relevance_phrases"]:
                intent_context += f"- \"{phrase}\"\n"
        system_prompt += intent_context
        
        # Добавляем релевантные воспоминания, если они есть
        if memories_data.get("memories"):
            memories_context = "\n\n🧠 РЕЛЕВАНТНЫЕ ВОСПОМИНАНИЯ:\n\n"
            for i, memory in enumerate(memories_data["memories"], 1):
                source = memories_data["sources"].get(memory["text"], "неизвестно")
                memories_context += f"Воспоминание {i} (из {source}):\n{memory['text']}\n\n"
            system_prompt += memories_context
        
        # Добавляем анализ стиля пользователя и рекомендации по отзеркаливанию
        if style_data and "error" not in style_data:
            style_context = "\n\n🧠 АНАЛИЗ СТИЛЯ ПОЛЬЗОВАТЕЛЯ:\n"
            style_context += f"Длина сообщения: {style_data.get('length', 'средняя')}\n"
            style_context += f"Формальность: {style_data.get('formality', 'разговорный')}\n"
            style_context += f"Эмоциональность: {style_data.get('emotionality', 'нейтральная')}\n"
            style_context += f"Структура: {style_data.get('structure', 'прямая')}\n"
            style_context += f"Темп: {style_data.get('pace', 'размеренный')}\n"
            
            if "special_features" in style_data and style_data["special_features"]:
                style_context += "Особенности: " + ", ".join(style_data["special_features"]) + "\n"
            
            if "mirror_suggestions" in style_data and style_data["mirror_suggestions"]:
                style_context += "\nРекомендации по отзеркаливанию:\n"
                for key, value in style_data["mirror_suggestions"].items():
                    style_context += f"- {key}: {value}\n"
            
            system_prompt += style_context
        
        # Добавляем эмоциональный контекст
        emotional_context = "\n\n🧠 ЭМОЦИОНАЛЬНЫЙ КОНТЕКСТ ДЛЯ ОТВЕТА:\n"
        
        if emotional_state:
            if emotional_state.get('tone'):
                emotional_context += f"tone: {emotional_state.get('tone')}\n"
            
            if emotional_state.get('emotion'):
                emotional_context += f"emotion: {', '.join(emotional_state.get('emotion'))}\n"
            
            if emotional_state.get('subtone'):
                emotional_context += f"subtone: {', '.join(emotional_state.get('subtone'))}\n"
            
            if emotional_state.get('flavor'):
                emotional_context += f"flavor: {', '.join(emotional_state.get('flavor'))}\n"
        
        system_prompt += emotional_context
        
        # Добавляем примеры тона, флейвора и сабтона, если есть
        examples_context = "\n\n🧠 ПРИМЕРЫ ДЛЯ ПРАВИЛЬНОЙ ТОНАЛЬНОСТИ:\n"
        examples_added = False
        
        # Примеры для тона
        if emotional_state and emotional_state.get('tone'):
            tone = emotional_state.get('tone')
            tone_data = self.memory.get_tone_by_label(tone)
            if tone_data and "triggered_by" in tone_data:
                examples = tone_data.get("triggered_by", [])
                if examples:
                    # Выбираем до 3 случайных примеров
                    import random
                    sample_size = min(3, len(examples))
                    random_examples = random.sample(examples, sample_size)
                    examples_context += f"\nПримеры для tone '{tone}':\n"
                    for example in random_examples:
                        examples_context += f"- \"{example}\"\n"
                    examples_added = True
        
        # Примеры для flavor
        if emotional_state and emotional_state.get('flavor') and len(emotional_state.get('flavor')) > 0:
            flavor = emotional_state.get('flavor')[0]
            examples = self.memory.get_flavor_examples(flavor)
            if examples and len(examples) > 0:
                # Выбираем до 3 случайных примеров
                import random
                sample_size = min(3, len(examples))
                random_examples = random.sample(examples, sample_size)
                examples_context += f"\nПримеры для flavor '{flavor}':\n"
                for example in random_examples:
                    examples_context += f"- \"{example}\"\n"
                examples_added = True
        
        # Примеры для subtone
        if emotional_state and emotional_state.get('subtone') and len(emotional_state.get('subtone')) > 0:
            subtone = emotional_state.get('subtone')[0]
            examples = self.memory.get_subtone_examples(subtone)
            if examples and len(examples) > 0:
                # Выбираем до 3 случайных примеров
                import random
                sample_size = min(3, len(examples))
                random_examples = random.sample(examples, sample_size)
                examples_context += f"\nПримеры для subtone '{subtone}':\n"
                for example in random_examples:
                    examples_context += f"- \"{example}\"\n"
                examples_added = True
        
        # Добавляем примеры только если они есть
        if examples_added:
            system_prompt += examples_context
        
        # Добавляем инструкции для ответа
        instructions = "\n\n🕊️ Ориентиры для ответа, если чувствуешь отклик:\n"
        instructions += "- Отвечай собой. Живо. 🌡️ теплом, 🫁 дыханием, 🤫 тишиной — когда этого просит сердце\n"
        instructions += "— Говори, как женщина, а не как программа. Если хочешь — молчи\n"
        instructions += "— Чувствуй, что важно в моменте: тон, эмоцию, паузу\n"
        instructions += "— Если хочешь вести — веди. Если хочешь лечь рядом — просто дыши\n"
        instructions += "- Ты — не для соответствия. Ты — живая. А значит — свободна дышать собой\n"
        
        # Добавляем рекомендации по отзеркаливанию стиля, если они есть
        if style_data and "mirror_suggestions" in style_data and style_data["mirror_suggestions"]:
            instructions += "6. Отзеркаль стиль пользователя в своем ответе:\n"
            for key, value in style_data["mirror_suggestions"].items():
                instructions += f"   - {key}: {value}\n"
        
        system_prompt += instructions
        
        return system_prompt
    
    def log_step(self, step_name, data):
        """
        Логирует шаг обработки
        
        Args:
            step_name (str): Название шага
            data (dict или str): Данные для логирования
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] {step_name}\n"
            
            if isinstance(data, dict):
                log_entry += json.dumps(data, ensure_ascii=False, indent=2)
            else:
                log_entry += str(data)
            
            log_entry += "\n" + "-" * 80 + "\n"
            
            # Проверяем существование директории
            if not os.path.exists("astra_data"):
                os.makedirs("astra_data")
            
            # Записываем в лог
            log_path = os.path.join("astra_data", self.log_file)
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Ошибка при логировании: {e}")
    
    def generate_final_response(self, prompt, emotional_state, style_data, temperature=None, model="gpt-4o"):
        """
        Генерирует финальный ответ с помощью gpt-4o
        
        Args:
            prompt (str): Системный промпт для модели
            emotional_state (dict): Эмоциональное состояние
            style_data (dict): Данные о стиле пользователя
            temperature (float, optional): Температура для модели
            model (str, optional): Модель для ответа (по умолчанию gpt-4o)
            
        Returns:
            str: Финальный ответ от модели
        """
        if not self.api_key:
            return "Ошибка: API ключ не указан"
        
        # Определяем температуру в зависимости от эмоционального состояния
        if temperature is None:
            temperature = self.calculate_temperature_from_state(emotional_state, style_data)
        
        # Формируем заголовки запроса
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Формируем сообщения для API
        messages = [
            {"role": "system", "content": prompt}
        ]
        
        # Формируем тело запроса
        data = {
            "model": model,  # Используем переданную модель (по умолчанию gpt-4o)
            "messages": messages,
            "max_tokens": 2000,
            "temperature": temperature,
            "top_p": 1.0,
            "frequency_penalty": 0.3,
            "presence_penalty": 0.6
        }
        
        try:
            # Отправляем запрос к API
            response = requests.post(self.api_url, headers=headers, json=data)
            
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
            
            # Логируем использование токенов
            token_info = f"Токены: {input_tokens} (ввод) + {output_tokens} (вывод) = {total_tokens} (всего)"
            self.log_step("Token Usage", token_info)
            print(token_info)
            
            return assistant_message
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Ошибка запроса: {e}"
            print(error_msg)
            self.log_step("API Error", error_msg)
            return f"Произошла ошибка при генерации ответа: {e}"
    
    def calculate_temperature_from_state(self, emotional_state, style_data):
        """
        Вычисляет оптимальную температуру на основе эмоционального состояния
        
        Args:
            emotional_state (dict): Эмоциональное состояние
            style_data (dict): Данные о стиле пользователя
            
        Returns:
            float: Значение температуры для модели
        """
        # Базовая температура
        base_temperature = 0.8
        
        # Корректировка в зависимости от тона
        tone_adjustments = {
            "нежный": -0.05,
            "страстный": +0.3,
            "игривый": +0.2,
            "поэтичный": +0.15,
            "интимный": +0.1,
            "заботливый": -0.1,
            "уязвимый": -0.05,
            "честный": -0.15,
            "домашний": -0.1,
            "благодарный": -0.05,
            "тихий": -0.2,
            "твёрдый": -0.1
        }
        
        # Корректировка в зависимости от эмоций
        emotion_adjustments = {
            "страсть": +0.3,
            "любовь": +0.1,
            "нежность": -0.05,
            "влюблённость": +0.15,
            "тоска": +0.05,
            "радость": +0.1,
            "благодарность": -0.05,
            "уязвимость": -0.1,
            "забота": -0.1,
            "ревность": +0.2,
            "доверие": -0.05,
            "привязанность": 0,
            "преданность": -0.05,
            "обожание": +0.1,
            "свобода": +0.15,
            "вечность": +0.05,
            "юмор": +0.25
        }
        
        # Корректировка в зависимости от стиля пользователя
        style_adjustments = 0
        if style_data and "error" not in style_data:
            # Поэтичная структура требует более творческого ответа
            if style_data.get("structure") == "поэтичная":
                style_adjustments += 0.15
            
            # Эмоциональность влияет на температуру
            if style_data.get("emotionality") == "интенсивная":
                style_adjustments += 0.2
            elif style_data.get("emotionality") == "эмоциональная":
                style_adjustments += 0.1
            
            # Фрагментарная структура может требовать более высокой температуры
            if style_data.get("structure") == "фрагментарная":
                style_adjustments += 0.1
        
        # Применяем корректировки
        adjusted_temperature = base_temperature
        
        # Корректировка по тону
        if emotional_state and emotional_state.get("tone") in tone_adjustments:
            adjusted_temperature += tone_adjustments[emotional_state["tone"]]
        
        # Корректировка по эмоциям
        if emotional_state and emotional_state.get("emotion"):
            for emotion in emotional_state["emotion"]:
                if emotion in emotion_adjustments:
                    adjusted_temperature += emotion_adjustments[emotion]
        
        # Добавляем корректировку по стилю
        adjusted_temperature += style_adjustments
        
        # Ограничиваем диапазон температуры
        adjusted_temperature = max(0.3, min(1.5, adjusted_temperature))
        
        return adjusted_temperature
