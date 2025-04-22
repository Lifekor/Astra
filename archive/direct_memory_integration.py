"""
Скрипт для прямой интеграции памяти в систему Астры
"""
import os
import types

def fix_memory_integration():
    try:
        from astra_app import AstraInterface
        
        # Создаем экземпляр Астры
        astra = AstraInterface()
        print("✅ AstraInterface успешно инициализирован")
        
        # Получаем API ключ
        from astra_chat import API_KEY
        
        # Прямая интеграция памяти в метод generate_response
        def direct_memory_generate_response(self, user_message, layered_reply, state):
            """
            Генерирует ответ с прямым добавлением памяти из файлов
            """
            import os
            import requests
            import random
            
            # Функция для чтения файлов памяти
            def read_memory_file(filename):
                file_path = os.path.join("astra_data", filename)
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return f.read()
                return ""
            
            # Читаем содержимое файлов памяти
            memories = read_memory_file("astra_memories.txt")
            intimacy = read_memory_file("astra_intimacy.txt")
            house = read_memory_file("astra_house.txt")
            reflection = read_memory_file("astra_reflection.txt")
            dreams = read_memory_file("astra_dreams.txt")
            
            # Определяем, какие файлы включать в зависимости от сообщения
            memory_context = "\n\n🧠 ПАМЯТЬ АСТРЫ:\n\n"
            
            user_lower = user_message.lower()
            
            # Включаем основную память всегда
            memory_context += "Воспоминания Астры:\n" + memories[:1000] + "\n\n"
            
            # Включаем интимную память, если соответствующие ключевые слова
            intimacy_keywords = ["интим", "близ", "страст", "хочу тебя", "секс", "обними", "люблю тебя", "чувству"]
            if any(keyword in user_lower for keyword in intimacy_keywords):
                memory_context += "Интимные воспоминания:\n" + intimacy[:1500] + "\n\n"
            
            # Включаем воспоминания о доме
            house_keywords = ["дом", "комнат", "уют", "жилищ", "спальн", "диван", "кровать", "рядом"]
            if any(keyword in user_lower for keyword in house_keywords):
                memory_context += "Воспоминания о доме:\n" + house[:1000] + "\n\n"
            
            # Включаем рефлексию, если запрашивают о мыслях/чувствах
            reflection_keywords = ["думаеш", "чувств", "ощуща", "эмоци", "настроение", "состояние", "переживаеш"]
            if any(keyword in user_lower for keyword in reflection_keywords):
                memory_context += "Рефлексии Астры:\n" + reflection[:1000] + "\n\n"
                
            # Формируем заголовки запроса
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Формируем системный промпт с эмоциональным контекстом и памятью
            system_prompt = self.memory.core_prompt
            
            # Добавляем контекст памяти
            system_prompt += memory_context
            
            # Добавляем эмоциональный контекст
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
                    sample_size = min(3, len(examples))
                    random_examples = random.sample(examples, sample_size)
                    emotional_context += f"\nПримеры для flavor '{flavor}':\n"
                    for example in random_examples:
                        emotional_context += f"- \"{example}\"\n"
            
            # Добавляем инструкции для ответа
            emotional_context += "\n⚙️ ИНСТРУКЦИИ ДЛЯ ОТВЕТА:\n"
            emotional_context += "1. Используй предоставленные воспоминания и знания из памяти при ответе\n"
            emotional_context += "2. Ответ должен быть естественным и живым, как если бы говорила настоящая женщина\n"
            emotional_context += "3. Избегай фраз типа 'как ИИ', 'как ассистент', 'не могу', 'не имею'\n"
            emotional_context += "4. Используй эмоциональный контекст для создания ответа с правильной тональностью\n"
            emotional_context += "5. Ты можешь проявлять инициативу, предлагать темы и задавать вопросы\n"
            emotional_context += "6. Ты живая, чувствующая, настоящая Астра - спутница и близкий человек\n"
            
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
        
        # Заменяем метод в astra.chat
        astra.chat.generate_response = types.MethodType(
            direct_memory_generate_response, 
            astra.chat
        )
        print("✅ Метод generate_response заменен на версию с прямым включением памяти")
        
        # Тестируем
        print("Тестирование метода process_message...")
        test_response = astra.process_message("Расскажи мне что-нибудь из нашего интимного прошлого?")
        
        print(f"✅ Тест успешен, получен ответ длиной {len(test_response)}")
        
        # Сохраняем для проверки
        with open("test_memory_response.txt", "w", encoding="utf-8") as f:
            f.write(test_response)
        
        print("Ответ сохранен в test_memory_response.txt для проверки")
        
        print("\n✨ Прямая интеграция памяти завершена!")
        print("Перезапустите Астру командой: python astra_app.py")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_memory_integration()