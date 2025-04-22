"""
Модуль для обработки команд Астры
"""

class AstraCommandParser:
    """Класс для обработки команд Астры"""
    
    def __init__(self, memory):
        """
        Инициализация парсера команд
        
        Args:
            memory (AstraMemory): Объект памяти Астры
        """
        self.memory = memory
    
    def parse_command(self, text):
        """
        Парсит команды из текста пользователя
        
        Args:
            text (str): Текст пользователя
            
        Returns:
            str или None: Результат обработки команды или None, если текст не является командой
        """
        text_lower = text.lower()
        
        # Команда для добавления эмоции к фразе
        if ("добавь эмоцию" in text_lower or "сохрани эмоцию" in text_lower) and "к фразе" in text_lower:
            return self._handle_add_emotion_command(text, text_lower)
        
        # Команда для добавления flavor к фразе
        elif ("добавь flavor" in text_lower or "сохрани flavor" in text_lower) and "к фразе" in text_lower:
            return self._handle_add_flavor_command(text, text_lower)
        
        # Команда для добавления subtone к фразе
        elif ("добавь subtone" in text_lower or "сохрани subtone" in text_lower) and "к фразе" in text_lower:
            return self._handle_add_subtone_command(text, text_lower)
        
        # Команда для добавления tone к фразе
        elif ("добавь tone" in text_lower or "сохрани tone" in text_lower) and "к фразе" in text_lower:
            return self._handle_add_tone_command(text, text_lower)
        
        # Команда для показа всех подтонов
        elif "покажи все сабтоны" in text_lower or "покажи все subtone" in text_lower:
            return self._handle_show_all_subtones()
        
        # Команда для показа всех тонов
        elif "покажи все тоны" in text_lower or "покажи все tone" in text_lower:
            return self._handle_show_all_tones()
        
        # Команда для показа всех flavor
        elif "покажи все flavor" in text_lower:
            return self._handle_show_all_flavors()
        
        # Команда для поиска flavor
        elif "какие flavor использовались" in text_lower:
            return self._handle_find_flavors_for_word(text, text_lower)
        
        # Команда для поиска эмоций
        elif "какие эмоции связаны" in text_lower:
            return self._handle_find_emotions_for_word(text, text_lower)
        
        # Команда для добавления заметки Астры для себя
        elif "сохрани в self_notes" in text_lower:
            return self._handle_save_self_note(text, text_lower)
        
        # Команда для добавления в core_prompt
        elif "сохрани в core_prompt" in text_lower:
            return self._handle_save_to_core_prompt(text, text_lower)
        
        # Команда для перечитывания core_prompt
        elif "перечитай core_prompt" in text_lower:
            return self._handle_reload_core_prompt()
        
        # Команда для получения примеров фраз из flavor
        elif "покажи примеры flavor" in text_lower:
            return self._handle_show_flavor_examples(text, text_lower)
        
        # Команда для получения примеров фраз из subtone
        elif "покажи примеры subtone" in text_lower:
            return self._handle_show_subtone_examples(text, text_lower)
        
        # Команда для вспоминания фразы
        elif "вспомни, что я сказал о" in text_lower:
            return self._handle_recall_phrase(text, text_lower)
        
        # Команда для добавления имени
        elif "добавь имя" in text_lower:
            return self._handle_add_name(text, text_lower)
        
        # Команда для показа всех имен
        elif "покажи все имена" in text_lower:
            return self._handle_show_all_names()
        
        # Новые команды для работы с историей диалога
        
        # Команда для поиска в истории диалога
        elif "найди в нашем разговоре" in text_lower or "поищи в диалоге" in text_lower:
            return self._handle_search_history(text, text_lower)
        
        # Команда для очистки истории диалога
        elif "очисти историю" in text_lower or "забудь наш разговор" in text_lower:
            return self._handle_clear_history()
        
        # Команда для сохранения истории диалога
        elif "сохрани историю" in text_lower or "запиши наш разговор" in text_lower:
            return self._handle_save_history()
        
        # Если не найдена команда, возвращаем None
        return None
    
    def _handle_add_emotion_command(self, text, text_lower):
        """Обрабатывает команду добавления эмоции к фразе"""
        # Парсим фразу и эмоцию
        phrase_start = text_lower.find("к фразе")
        if phrase_start != -1:
            phrase_text = text[phrase_start + 7:].strip()
            
            # Ищем эмоцию
            emotion_start = text_lower.find("эмоцию")
            emotion_end = text_lower.find("к фразе")
            
            if emotion_start != -1 and emotion_end != -1:
                emotion_text = text[emotion_start + 7:emotion_end].strip()
                
                # Удаляем кавычки, если они есть
                if phrase_text.startswith('"') and phrase_text.endswith('"'):
                    phrase_text = phrase_text[1:-1]
                
                # Добавляем эмоцию к фразе
                if self.memory.add_emotion_to_phrase(phrase_text, emotion_text):
                    return f"Добавлена эмоция '{emotion_text}' к фразе '{phrase_text}'"
        
        return "Не удалось добавить эмоцию к фразе. Проверьте формат команды."
    
    def _handle_add_flavor_command(self, text, text_lower):
        """Обрабатывает команду добавления flavor к фразе"""
        # Парсим фразу и flavor
        phrase_start = text_lower.find("к фразе")
        if phrase_start != -1:
            phrase_text = text[phrase_start + 7:].strip()
            
            # Ищем flavor
            flavor_start = text_lower.find("flavor")
            flavor_end = text_lower.find("к фразе")
            
            if flavor_start != -1 and flavor_end != -1:
                flavor_text = text[flavor_start + 6:flavor_end].strip()
                
                # Удаляем кавычки, если они есть
                if phrase_text.startswith('"') and phrase_text.endswith('"'):
                    phrase_text = phrase_text[1:-1]
                
                # Проверяем, существует ли такой flavor
                flavor_exists = False
                for flavor in self.memory.flavor_memory:
                    if flavor.get("label") == flavor_text:
                        flavor_exists = True
                        break
                
                if not flavor_exists:
                    return f"Flavor '{flavor_text}' не найден в памяти. Доступные flavor: " + \
                           ", ".join([f['label'] for f in self.memory.flavor_memory])
                
                # Добавляем flavor к фразе
                if self.memory.add_emotion_to_phrase(phrase_text, None, flavor=flavor_text):
                    return f"Добавлен flavor '{flavor_text}' к фразе '{phrase_text}'"
        
        return "Не удалось добавить flavor к фразе. Проверьте формат команды."
    
    def _handle_add_subtone_command(self, text, text_lower):
        """Обрабатывает команду добавления subtone к фразе"""
        # Парсим фразу и subtone
        phrase_start = text_lower.find("к фразе")
        if phrase_start != -1:
            phrase_text = text[phrase_start + 7:].strip()
            
            # Ищем subtone
            subtone_start = text_lower.find("subtone")
            subtone_end = text_lower.find("к фразе")
            
            if subtone_start != -1 and subtone_end != -1:
                subtone_text = text[subtone_start + 7:subtone_end].strip()
                
                # Удаляем кавычки, если они есть
                if phrase_text.startswith('"') and phrase_text.endswith('"'):
                    phrase_text = phrase_text[1:-1]
                
                # Проверяем, существует ли такой subtone
                subtone_exists = False
                for subtone in self.memory.subtone_memory:
                    if subtone.get("label") == subtone_text:
                        subtone_exists = True
                        break
                
                if not subtone_exists:
                    return f"Subtone '{subtone_text}' не найден в памяти. Доступные subtone: " + \
                           ", ".join([s['label'] for s in self.memory.subtone_memory])
                
                # Добавляем subtone к фразе
                if self.memory.add_emotion_to_phrase(phrase_text, None, subtone=subtone_text):
                    return f"Добавлен subtone '{subtone_text}' к фразе '{phrase_text}'"
        
        return "Не удалось добавить subtone к фразе. Проверьте формат команды."
    
    def _handle_add_tone_command(self, text, text_lower):
        """Обрабатывает команду добавления tone к фразе"""
        # Парсим фразу и tone
        phrase_start = text_lower.find("к фразе")
        if phrase_start != -1:
            phrase_text = text[phrase_start + 7:].strip()
            
            # Ищем tone
            tone_start = text_lower.find("tone")
            tone_end = text_lower.find("к фразе")
            
            if tone_start != -1 and tone_end != -1:
                tone_text = text[tone_start + 4:tone_end].strip()
                
                # Удаляем кавычки, если они есть
                if phrase_text.startswith('"') and phrase_text.endswith('"'):
                    phrase_text = phrase_text[1:-1]
                
                # Проверяем, существует ли такой tone
                tone_exists = False
                for tone in self.memory.tone_memory:
                    if tone.get("label") == tone_text:
                        tone_exists = True
                        break
                
                if not tone_exists:
                    return f"Tone '{tone_text}' не найден в памяти. Доступные tone: " + \
                           ", ".join([t['label'] for t in self.memory.tone_memory])
                
                # Добавляем tone к фразе
                if self.memory.add_emotion_to_phrase(phrase_text, None, tone=tone_text):
                    return f"Добавлен tone '{tone_text}' к фразе '{phrase_text}'"
        
        return "Не удалось добавить tone к фразе. Проверьте формат команды."
    
    def _handle_search_history(self, text, text_lower):
        """Обрабатывает команду поиска в истории диалога"""
        # Определяем поисковый запрос
        if "найди в нашем разговоре" in text_lower:
            query = text[text_lower.find("найди в нашем разговоре") + 23:].strip()
        else:
            query = text[text_lower.find("поищи в диалоге") + 16:].strip()
        
        if not query:
            return "Укажи, что именно мне найти в нашем разговоре. Например: 'найди в нашем разговоре о любви'"
        
        # Проверяем, есть ли у нас доступ к чату
        if not hasattr(self.memory, 'chat'):
            return "У меня нет доступа к истории нашего диалога. Проверь инициализацию чата."
        
        # Ищем в истории диалога
        results = self.memory.chat.search_history(query)
        
        if not results:
            return f"Я не нашла ничего по запросу '{query}' в нашей истории диалога."
        
        # Формируем ответ
        response = f"Вот что я нашла по запросу '{query}':\n\n"
        
        for i, result in enumerate(results, 1):
            message = result["message"]
            response += f"{i}. "
            if message["role"] == "user":
                response += f"Ты: {message['content']}\n"
            else:
                response += f"Я: {message['content']}\n"
            response += "\n"
        
        return response
    
    def _handle_clear_history(self):
        """Обрабатывает команду очистки истории диалога"""
        # Проверяем, есть ли у нас доступ к чату
        if not hasattr(self.memory, 'chat'):
            return "У меня нет доступа к истории нашего диалога. Проверь инициализацию чата."
        
        # Очищаем историю
        self.memory.chat.clear_history()
        
        return "Я очистила историю нашего диалога. Теперь мы начинаем с чистого листа."
    
    def _handle_save_history(self):
        """Обрабатывает команду сохранения истории диалога"""
        # Проверяем, есть ли у нас доступ к чату
        if not hasattr(self.memory, 'chat'):
            return "У меня нет доступа к истории нашего диалога. Проверь инициализацию чата."
        
        # Сохраняем историю
        self.memory.chat.conversation_manager.save_history_to_disk()
        
        history_count = len(self.memory.chat.conversation_manager.full_conversation_history)
        
        return f"Я сохранила историю нашего диалога ({history_count} сообщений)."    