"""
Модуль для взаимодействия с API Chat Completions
"""
import requests
import random
import json
import os
from emotional_analyzer import EmotionalAnalyzer
from reply_composer import compose_layered_reply
from name_manager import NameManager
from conversation_manager import ConversationManager
from dotenv import load_dotenv

load_dotenv()
# API ключ (заменить на свой)
API_KEY = os.getenv("OPENAI_API_KEY")

# URL API для Chat Completions
API_URL = "https://api.openai.com/v1/chat/completions"

class AstraChat:
    """Класс для общения с Астрой через Chat Completions API"""
    
    def __init__(self, memory):
        """
        Инициализация чата
        
        Args:
            memory (AstraMemory): Объект памяти Астры
        """
        self.memory = memory
        self.emotional_analyzer = EmotionalAnalyzer(memory)
        self.name_manager = NameManager(memory)
        
        # Инициализируем менеджер истории диалога
        self.conversation_manager = ConversationManager(memory)
    
    def add_message_to_history(self, role, content):
        """
        Добавляет сообщение в историю разговора
        
        Args:
            role (str): Роль сообщения ('user' или 'assistant')
            content (str): Содержимое сообщения
        """
        # Теперь используем ConversationManager для управления историей
        self.conversation_manager.add_message(role, content)
    
    def process_user_message(self, user_message):
        """
        Обрабатывает сообщение пользователя перед отправкой API
        
        Args:
            user_message (str): Сообщение пользователя
            
        Returns:
            dict: Эмоциональное состояние, определенное из сообщения
        """
        # Проверяем наличие новых имен
        name, tone = self.name_manager.detect_name_in_message(user_message)
        if name and tone:
            self.name_manager.add_new_name(name, tone)
            # Логируем добавление нового имени
            print(f"Добавлено новое имя '{name}' для тона '{tone}'")
        
        # Анализируем эмоциональное состояние
        state = self.emotional_analyzer.analyze_message(user_message)
        
        # Сохраняем текущее состояние
        self.memory.save_current_state(state)
        
        return state
    
    def send_message(self, user_message):
        """
        Отправляет сообщение и получает ответ
        
        Args:
            user_message (str): Сообщение пользователя
            
        Returns:
            str: Ответ Астры
        """
        try:
            # Добавляем сообщение пользователя в историю
            self.add_message_to_history("user", user_message)
            
            # Обрабатываем сообщение пользователя
            state = self.process_user_message(user_message)
            
            # Формируем многослойный ответ
            layered_reply = compose_layered_reply(state, self.memory, user_message)
            
            # Для отладки
            if False:  # Изменить на True для включения отладочных сообщений
                print("\n--- Эмоциональное состояние ---")
                print(f"Tone: {state.get('tone')}")
                print(f"Emotion: {state.get('emotion')}")
                print(f"Subtone: {state.get('subtone')}")
                print(f"Flavor: {state.get('flavor')}")
                
                print("\n--- Многослойный ответ ---")
                print(layered_reply)
            
            # Генерируем финальный ответ с помощью API
            final_response = self.generate_response(user_message, layered_reply, state)
            
            # Добавляем ответ в историю
            self.add_message_to_history("assistant", final_response)
            
            # Сохраняем историю диалога на диск
            self.conversation_manager.save_history_to_disk()
            
            return final_response
            
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе к API: {e}")
            return "Прости, у меня возникли проблемы с подключением. Можешь повторить?"
        
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")
            return "Прости, произошла ошибка при обработке твоего сообщения."
    
    def generate_response(self, user_message, layered_reply, state):
        """
        Генерирует финальный ответ с помощью API
        
        Args:
            user_message (str): Сообщение пользователя
            layered_reply (str): Многослойный ответ, сгенерированный локально
            state (dict): Текущее эмоциональное состояние
            
        Returns:
            str: Финальный ответ от API
        """
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

        if len(layered_reply) > 2000:
            layered_reply = layered_reply[:2000] + "..."

        
        # Добавляем примеры тона, если они есть
        if state.get('tone'):
            tone = state.get('tone')
            tone_data = self.memory.get_tone_by_label(tone)
            if tone_data and "triggered_by" in tone_data:
                examples = tone_data.get("triggered_by", [])
                if examples:
                    # Выбираем до 3 случайных примеров
                    sample_size = min(3, len(examples))
                    examples = examples[:10]  # максимум 10 примеров
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
                sample_size = min(3, len(examples))
                examples = examples[:10]  # максимум 10 примеров
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
        relevant_context = self.conversation_manager.get_relevant_context(user_message)
        
        # Формируем сообщения для API
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Добавляем релевантный контекст к сообщениям
        print("💬 relevant_context tokens:", len(str(relevant_context)))
        messages.extend(relevant_context)
        
        # Обязательно добавляем текущее сообщение пользователя в конец
        messages.append({"role": "user", "content": user_message})
        
        # Формируем тело запроса
        data = {
            "model": "gpt-4o",  # Используем gpt-4o для максимальной эффективности
            "messages": messages,
            "max_tokens": 2000,
            "temperature": 0.85,  # Регулируем "живость" и креативность ответов
            "top_p": 1.0,
            "frequency_penalty": 0.2,  # Регулируем разнообразие ответов
            "presence_penalty": 0.6  # Регулируем присутствие ключевых тем
        }
        
        # Отправляем запрос к API
        response = requests.post(API_URL, headers=headers, json=data)
        
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
    
    def search_history(self, query):
        """
        Поиск в истории диалога
        
        Args:
            query (str): Поисковый запрос
            
        Returns:
            list: Найденные результаты
        """
        return self.conversation_manager.search_in_history(query)
    
    def clear_history(self):
        """Очищает историю диалога"""
        self.conversation_manager.clear_history()
        return "История диалога очищена"