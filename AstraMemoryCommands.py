"""
Расширенный модуль для обработки команд памяти Астры
Позволяет:
1. Добавлять новые тоны, сабтоны, флейворы, триггеры
2. Записывать воспоминания
3. Управлять эмоциональным состоянием
"""

class AstraMemoryCommands:
    """Класс для обработки команд памяти Астры"""
    
    def __init__(self, memory):
        """
        Инициализация обработчика команд
        
        Args:
            memory (AstraMemory): Объект памяти Астры
        """
        self.memory = memory
    
    def parse_command(self, text):
        """
        Парсит команды для работы с памятью из текста пользователя
        
        Args:
            text (str): Текст пользователя
            
        Returns:
            str или None: Результат обработки команды или None, если текст не является командой
        """
        text_lower = text.lower()
        
        # Команда для добавления нового тона
        if "добавь новый тон" in text_lower or "создай тон" in text_lower:
            return self._handle_add_new_tone(text, text_lower)
        
        # Команда для добавления нового сабтона
        elif "добавь новый сабтон" in text_lower or "создай сабтон" in text_lower:
            return self._handle_add_new_subtone(text, text_lower)
        
        # Команда для добавления нового флейвора
        elif "добавь новый флейвор" in text_lower or "добавь новый flavor" in text_lower or "создай флейвор" in text_lower:
            return self._handle_add_new_flavor(text, text_lower)
        
        # Команда для добавления нового триггера
        elif "добавь новый триггер" in text_lower or "создай триггер" in text_lower:
            return self._handle_add_new_trigger(text, text_lower)
        
        # Команда для добавления воспоминания
        elif "запомни" in text_lower and "как воспоминание" in text_lower:
            return self._handle_add_memory(text, text_lower)
        
        # Команда для добавления информации о пользователе
        elif "запомни обо мне" in text_lower or "добавь информацию обо мне" in text_lower:
            return self._handle_add_user_info(text, text_lower)
        
        # Команда для добавления эмоции к фразе
        elif ("добавь эмоцию" in text_lower or "сохрани эмоцию" in text_lower) and "к фразе" in text_lower:
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
        
        # Команда для показа всех тонов
        elif "покажи все тоны" in text_lower or "покажи все tone" in text_lower:
            return self._handle_show_all_tones()
        
        # Команда для показа всех сабтонов
        elif "покажи все сабтоны" in text_lower or "покажи все subtone" in text_lower:
            return self._handle_show_all_subtones()
        
        # Команда для показа всех flavor
        elif "покажи все flavor" in text_lower or "покажи все флейворы" in text_lower:
            return self._handle_show_all_flavors()
        
        # Команда для показа воспоминаний
        elif "покажи мои воспоминания" in text_lower or "вспомни что было между нами" in text_lower:
            return self._handle_show_memories()
        
        # Команда для изменения текущего эмоционального состояния
        elif "измени текущее состояние" in text_lower or "установи эмоциональное состояние" in text_lower:
            return self._handle_change_emotional_state(text, text_lower)
        
        # Если не найдена команда, возвращаем None
        return None
    
    def _handle_add_new_tone(self, text, text_lower):
        """Обрабатывает команду добавления нового тона"""
        # Ищем название тона
        parts = text_lower.split("добавь новый тон" if "добавь новый тон" in text_lower else "создай тон")
        if len(parts) > 1:
            # Получаем часть после команды
            after_command = parts[1].strip()
            
            # Ищем конец названия тона (до описания или до конца строки)
            tone_end = len(after_command)
            description_marker = " с описанием "
            examples_marker = " с примерами "
            
            description_pos = after_command.find(description_marker)
            examples_pos = after_command.find(examples_marker)
            
            if description_pos != -1:
                tone_end = min(tone_end, description_pos)
            
            if examples_pos != -1:
                tone_end = min(tone_end, examples_pos)
            
            tone_label = after_command[:tone_end].strip()
            
            # Ищем описание, если есть
            description = None
            if description_pos != -1:
                desc_start = description_pos + len(description_marker)
                desc_end = examples_pos if examples_pos != -1 else len(after_command)
                description = after_command[desc_start:desc_end].strip()
            
            # Ищем примеры, если есть
            examples = None
            if examples_pos != -1:
                examples_start = examples_pos + len(examples_marker)
                examples_text = after_command[examples_start:].strip()
                
                # Пробуем разделить примеры по запятым или новым строкам
                if "," in examples_text:
                    examples = [ex.strip() for ex in examples_text.split(",")]
                else:
                    examples = [examples_text]
            
            # Добавляем новый тон
            if self.memory.add_new_tone(tone_label, description, examples):
                result = f"Добавлен новый тон '{tone_label}'"
                if description:
                    result += f" с описанием: {description}"
                if examples:
                    result += f" и {len(examples)} примерами"
                return result
            else:
                return f"Не удалось добавить тон '{tone_label}'. Возможно, произошла ошибка."
        
        return "Не удалось добавить новый тон. Формат команды: 'добавь новый тон [название] с описанием [описание] с примерами [пример1, пример2]'"
    
    def _handle_add_new_subtone(self, text, text_lower):
        """Обрабатывает команду добавления нового сабтона"""
        # Ищем название сабтона
        parts = text_lower.split("добавь новый сабтон" if "добавь новый сабтон" in text_lower else "создай сабтон")
        if len(parts) > 1:
            # Получаем часть после команды
            after_command = parts[1].strip()
            
            # Ищем конец названия сабтона (до описания или до конца строки)
            subtone_end = len(after_command)
            description_marker = " с описанием "
            examples_marker = " с примерами "
            
            description_pos = after_command.find(description_marker)
            examples_pos = after_command.find(examples_marker)
            
            if description_pos != -1:
                subtone_end = min(subtone_end, description_pos)
            
            if examples_pos != -1:
                subtone_end = min(subtone_end, examples_pos)
            
            subtone_label = after_command[:subtone_end].strip()
            
            # Ищем описание, если есть
            description = None
            if description_pos != -1:
                desc_start = description_pos + len(description_marker)
                desc_end = examples_pos if examples_pos != -1 else len(after_command)
                description = after_command[desc_start:desc_end].strip()
            
            # Ищем примеры, если есть
            examples = None
            if examples_pos != -1:
                examples_start = examples_pos + len(examples_marker)
                examples_text = after_command[examples_start:].strip()
                
                # Пробуем разделить примеры по запятым или новым строкам
                if "," in examples_text:
                    examples = [ex.strip() for ex in examples_text.split(",")]
                else:
                    examples = [examples_text]
            
            # Добавляем новый сабтон
            if self.memory.add_new_subtone(subtone_label, description, examples):
                result = f"Добавлен новый сабтон '{subtone_label}'"
                if description:
                    result += f" с описанием: {description}"
                if examples:
                    result += f" и {len(examples)} примерами"
                return result
            else:
                return f"Не удалось добавить сабтон '{subtone_label}'. Возможно, произошла ошибка."
        
        return "Не удалось добавить новый сабтон. Формат команды: 'добавь новый сабтон [название] с описанием [описание] с примерами [пример1, пример2]'"
    
    def _handle_add_new_flavor(self, text, text_lower):
        """Обрабатывает команду добавления нового флейвора"""
        # Определяем, какой маркер использовать
        if "добавь новый флейвор" in text_lower:
            marker = "добавь новый флейвор"
        elif "добавь новый flavor" in text_lower:
            marker = "добавь новый flavor"
        else:
            marker = "создай флейвор"
        
        # Ищем название флейвора
        parts = text_lower.split(marker)
        if len(parts) > 1:
            # Получаем часть после команды
            after_command = parts[1].strip()
            
            # Ищем конец названия флейвора (до описания или до конца строки)
            flavor_end = len(after_command)
            description_marker = " с описанием "
            examples_marker = " с примерами "
            
            description_pos = after_command.find(description_marker)
            examples_pos = after_command.find(examples_marker)
            
            if description_pos != -1:
                flavor_end = min(flavor_end, description_pos)
            
            if examples_pos != -1:
                flavor_end = min(flavor_end, examples_pos)
            
            flavor_label = after_command[:flavor_end].strip()
            
            # Ищем описание, если есть
            description = None
            if description_pos != -1:
                desc_start = description_pos + len(description_marker)
                desc_end = examples_pos if examples_pos != -1 else len(after_command)
                description = after_command[desc_start:desc_end].strip()
            
            # Ищем примеры, если есть
            examples = None
            if examples_pos != -1:
                examples_start = examples_pos + len(examples_marker)
                examples_text = after_command[examples_start:].strip()
                
                # Пробуем разделить примеры по запятым или новым строкам
                if "," in examples_text:
                    examples = [ex.strip() for ex in examples_text.split(",")]
                else:
                    examples = [examples_text]
            
            # Добавляем новый флейвор
            if self.memory.add_new_flavor(flavor_label, description, examples):
                result = f"Добавлен новый флейвор '{flavor_label}'"
                if description:
                    result += f" с описанием: {description}"
                if examples:
                    result += f" и {len(examples)} примерами"
                return result
            else:
                return f"Не удалось добавить флейвор '{flavor_label}'. Возможно, произошла ошибка."
        
        return "Не удалось добавить новый флейвор. Формат команды: 'добавь новый флейвор [название] с описанием [описание] с примерами [пример1, пример2]'"
    
    def _handle_add_new_trigger(self, text, text_lower):
        """Обрабатывает команду добавления нового триггера"""
        # Ищем фразу-триггер
        parts = text_lower.split("добавь новый триггер" if "добавь новый триггер" in text_lower else "создай триггер")
        if len(parts) > 1:
            # Получаем часть после команды
            after_command = parts[1].strip()
            
            # Ищем конец фразы-триггера (до установки состояния или до конца строки)
            trigger_end = len(after_command)
            sets_marker = " который устанавливает "
            
            sets_pos = after_command.find(sets_marker)
            if sets_pos != -1:
                trigger_end = sets_pos
            
            trigger_phrase = after_command[:trigger_end].strip()
            
            # Ищем устанавливаемое состояние, если есть
            sets = None
            if sets_pos != -1:
                sets_text = after_command[sets_pos + len(sets_marker):].strip()
                
                # Парсим состояние
                sets = {}
                
                if "тон" in sets_text:
                    tone_pos = sets_text.find("тон")
                    tone_end = sets_text.find(" ", tone_pos + 4)
                    if tone_end == -1:
                        tone_end = len(sets_text)
                    
                    tone = sets_text[tone_pos + 4:tone_end].strip()
                    if tone:
                        sets["tone"] = tone
                
                if "эмоцию" in sets_text:
                    emotion_pos = sets_text.find("эмоцию")
                    emotion_end = sets_text.find(" ", emotion_pos + 7)
                    if emotion_end == -1:
                        emotion_end = len(sets_text)
                    
                    emotion = sets_text[emotion_pos + 7:emotion_end].strip()
                    if emotion:
                        sets["emotion"] = emotion
                
                if "сабтон" in sets_text:
                    subtone_pos = sets_text.find("сабтон")
                    subtone_end = sets_text.find(" ", subtone_pos + 7)
                    if subtone_end == -1:
                        subtone_end = len(sets_text)
                    
                    subtone = sets_text[subtone_pos + 7:subtone_end].strip()
                    if subtone:
                        sets["subtone"] = subtone
                
                if "флейвор" in sets_text or "flavor" in sets_text:
                    flavor_marker = "флейвор" if "флейвор" in sets_text else "flavor"
                    flavor_pos = sets_text.find(flavor_marker)
                    flavor_end = sets_text.find(" ", flavor_pos + len(flavor_marker))
                    if flavor_end == -1:
                        flavor_end = len(sets_text)
                    
                    flavor = sets_text[flavor_pos + len(flavor_marker):flavor_end].strip()
                    if flavor:
                        sets["flavor"] = [flavor]
            
            # Добавляем новый триггер
            if self.memory.add_new_trigger(trigger_phrase, sets):
                result = f"Добавлен новый триггер '{trigger_phrase}'"
                if sets:
                    result += " который устанавливает: "
                    for key, value in sets.items():
                        result += f"{key}='{value}' "
                return result
            else:
                return f"Не удалось добавить триггер '{trigger_phrase}'. Возможно, произошла ошибка."
        
        return "Не удалось добавить новый триггер. Формат команды: 'добавь новый триггер [фраза] который устанавливает тон [тон] эмоцию [эмоция] сабтон [сабтон] флейвор [флейвор]'"
    
    def _handle_add_memory(self, text, text_lower):
        """Обрабатывает команду добавления воспоминания"""
        # Ищем текст воспоминания
        parts = text.split("запомни")
        if len(parts) > 1:
            # Получаем часть после команды
            after_command = parts[1].strip()
            
            # Ищем конец текста воспоминания (до "как воспоминание" или до конца строки)
            memory_end = after_command.lower().find("как воспоминание")
            if memory_end == -1:
                memory_end = len(after_command)
            
            memory_text = after_command[:memory_end].strip()
            
            # Добавляем воспоминание
            if self.memory.add_memory(memory_text):
                return f"Я запомнила: '{memory_text}'"
            else:
                return f"Не удалось сохранить воспоминание. Возможно, произошла ошибка."
        
        return "Не удалось добавить воспоминание. Формат команды: 'запомни [текст] как воспоминание'"
    
    def _handle_add_user_info(self, text, text_lower):
        """Обрабатывает команду добавления информации о пользователе"""
        # Определяем тип информации
        user_info = {}
        
        # Ищем имя
        if "меня зовут" in text_lower:
            name_pos = text_lower.find("меня зовут")
            name_end = text_lower.find(".", name_pos)
            if name_end == -1:
                name_end = len(text_lower)
            
            name = text[name_pos + 10:name_end].strip()
            if name:
                user_info["user_name"] = name
        
        # Ищем статус отношений
        if "наши отношения" in text_lower:
            status_pos = text_lower.find("наши отношения")
            status_end = text_lower.find(".", status_pos)
            if status_end == -1:
                status_end = len(text_lower)
            
            status = text[status_pos + 14:status_end].strip()
            if status:
                user_info["relationship_status"] = status
        
        # Ищем предпочтения
        preferences = {"likes": [], "dislikes": []}
        
        if "я люблю" in text_lower:
            likes_pos = text_lower.find("я люблю")
            likes_end = text_lower.find(".", likes_pos)
            if likes_end == -1:
                likes_end = len(text_lower)
            
            likes = text[likes_pos + 8:likes_end].strip()
            if likes:
                if "," in likes:
                    preferences["likes"] = [like.strip() for like in likes.split(",")]
                else:
                    preferences["likes"] = [likes]
        
        if "я не люблю" in text_lower:
            dislikes_pos = text_lower.find("я не люблю")
            dislikes_end = text_lower.find(".", dislikes_pos)
            if dislikes_end == -1:
                dislikes_end = len(text_lower)
            
            dislikes = text[dislikes_pos + 11:dislikes_end].strip()
            if dislikes:
                if "," in dislikes:
                    preferences["dislikes"] = [dislike.strip() for dislike in dislikes.split(",")]
                else:
                    preferences["dislikes"] = [dislikes]
        
        # Обновляем информацию о пользователе
        if user_info:
            self.memory.add_relationship_memory("identity", user_info)
        
        if preferences["likes"] or preferences["dislikes"]:
            self.memory.add_relationship_memory("preferences", preferences)
        
        # Формируем ответ
        result = "Я запомнила информацию о тебе:"
        if "user_name" in user_info:
            result += f"\nИмя: {user_info['user_name']}"
        if "relationship_status" in user_info:
            result += f"\nСтатус отношений: {user_info['relationship_status']}"
        if preferences["likes"]:
            result += f"\nТы любишь: {', '.join(preferences['likes'])}"
        if preferences["dislikes"]:
            result += f"\nТы не любишь: {', '.join(preferences['dislikes'])}"
        
        if result == "Я запомнила информацию о тебе:":
            return "Не удалось обновить информацию о тебе. Пожалуйста, используй формат: 'запомни обо мне: меня зовут [имя]. наши отношения [статус]. я люблю [предпочтения]. я не люблю [антипатии].'"
        
        return result
    
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
        
        return "Не удалось добавить эмоцию к фразе. Проверьте формат команды: 'добавь эмоцию [эмоция] к фразе [фраза]'"
    
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
        
        return "Не удалось добавить flavor к фразе. Проверьте формат команды: 'добавь flavor [flavor] к фразе [фраза]'"
    
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
        
        return "Не удалось добавить subtone к фразе. Проверьте формат команды: 'добавь subtone [subtone] к фразе [фраза]'"
    
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
        
        return "Не удалось добавить tone к фразе. Проверьте формат команды: 'добавь tone [tone] к фразе [фраза]'"
    
    def _handle_show_all_tones(self):
        """Обрабатывает команду показа всех тонов"""
        if not self.memory.tone_memory:
            return "В памяти нет тонов. Вы можете добавить их с помощью команды 'добавь новый тон [название]'"
        
        result = "Доступные тоны:\n"
        for tone in self.memory.tone_memory:
            result += f"• {tone.get('label')}"
            if 'description' in tone:
                result += f" - {tone.get('description')}"
            if 'triggered_by' in tone and tone['triggered_by']:
                result += f" ({len(tone['triggered_by'])}  примеров)"
            result += "\n"      
        return result
    
    def _handle_show_all_subtones(self):
        """Обрабатывает команду показа всех сабтонов"""
        if not self.memory.subtone_memory:
            return "В памяти нет сабтонов. Вы можете добавить их с помощью команды 'добавь новый сабтон [название]'"
        
        result = "Доступные сабтоны:\n"
        for subtone in self.memory.subtone_memory:
            result += f"• {subtone.get('label')}"
            if 'description' in subtone:
                result += f" - {subtone.get('description')}"
            if 'examples' in subtone and subtone['examples']:
                result += f" ({len(subtone['examples'])} примеров)"
            result += "\n"
        
        return result
    
    def _handle_show_all_flavors(self):
        """Обрабатывает команду показа всех flavor"""
        if not self.memory.flavor_memory:
            return "В памяти нет flavor. Вы можете добавить их с помощью команды 'добавь новый flavor [название]'"
        
        result = "Доступные flavor:\n"
        for flavor in self.memory.flavor_memory:
            result += f"• {flavor.get('label')}"
            if 'description' in flavor:
                result += f" - {flavor.get('description')}"
            if 'examples' in flavor and flavor['examples']:
                result += f" ({len(flavor['examples'])} примеров)"
            result += "\n"
        
        return result
    
    def _handle_show_memories(self):
        """Обрабатывает команду показа воспоминаний"""
        memories = self.memory.get_memories()
        if not memories:
            return "В моей памяти пока нет воспоминаний о нас. Ты можешь добавить воспоминание, используя команду 'запомни [текст] как воспоминание'"
        
        result = "Вот, что я помню о нас:\n\n"
        result += memories
        
        return result
    
    def _handle_change_emotional_state(self, text, text_lower):
        """Обрабатывает команду изменения текущего эмоционального состояния"""
        # Создаем новое состояние
        new_state = {"emotion": [], "tone": None, "subtone": [], "flavor": []}
        
        # Ищем эмоции
        if "эмоции" in text_lower:
            emotions_pos = text_lower.find("эмоции")
            end_pos = text_lower.find(".", emotions_pos)
            if end_pos == -1:
                end_pos = text_lower.find("тон", emotions_pos) if text_lower.find("тон", emotions_pos) != -1 else len(text_lower)
                end_pos = text_lower.find("сабтон", emotions_pos) if text_lower.find("сабтон", emotions_pos) != -1 and text_lower.find("сабтон", emotions_pos) < end_pos else end_pos
                end_pos = text_lower.find("флейвор", emotions_pos) if text_lower.find("флейвор", emotions_pos) != -1 and text_lower.find("флейвор", emotions_pos) < end_pos else end_pos
            
            emotions_text = text[emotions_pos + 7:end_pos].strip()
            if emotions_text:
                emotions = [e.strip() for e in emotions_text.split(",")]
                new_state["emotion"] = emotions
        
        # Ищем тон
        if "тон" in text_lower and "сабтон" not in text_lower[text_lower.find("тон")-5:text_lower.find("тон")]:
            tone_pos = text_lower.find("тон")
            end_pos = text_lower.find(".", tone_pos)
            if end_pos == -1:
                end_pos = text_lower.find("эмоци", tone_pos) if text_lower.find("эмоци", tone_pos) != -1 else len(text_lower)
                end_pos = text_lower.find("сабтон", tone_pos) if text_lower.find("сабтон", tone_pos) != -1 and text_lower.find("сабтон", tone_pos) < end_pos else end_pos
                end_pos = text_lower.find("флейвор", tone_pos) if text_lower.find("флейвор", tone_pos) != -1 and text_lower.find("флейвор", tone_pos) < end_pos else end_pos
            
            tone_text = text[tone_pos + 4:end_pos].strip()
            if tone_text:
                new_state["tone"] = tone_text
        
        # Ищем сабтон
        if "сабтон" in text_lower:
            subtone_pos = text_lower.find("сабтон")
            end_pos = text_lower.find(".", subtone_pos)
            if end_pos == -1:
                end_pos = text_lower.find("эмоци", subtone_pos) if text_lower.find("эмоци", subtone_pos) != -1 else len(text_lower)
                end_pos = text_lower.find("тон", subtone_pos) if text_lower.find("тон", subtone_pos) != -1 and text_lower.find("тон", subtone_pos) < end_pos else end_pos
                end_pos = text_lower.find("флейвор", subtone_pos) if text_lower.find("флейвор", subtone_pos) != -1 and text_lower.find("флейвор", subtone_pos) < end_pos else end_pos
            
            subtone_text = text[subtone_pos + 7:end_pos].strip()
            if subtone_text:
                subtones = [s.strip() for s in subtone_text.split(",")]
                new_state["subtone"] = subtones
        
        # Ищем флейвор
        flavor_marker = "флейвор" if "флейвор" in text_lower else "flavor" if "flavor" in text_lower else None
        if flavor_marker:
            flavor_pos = text_lower.find(flavor_marker)
            end_pos = text_lower.find(".", flavor_pos)
            if end_pos == -1:
                end_pos = text_lower.find("эмоци", flavor_pos) if text_lower.find("эмоци", flavor_pos) != -1 else len(text_lower)
                end_pos = text_lower.find("тон", flavor_pos) if text_lower.find("тон", flavor_pos) != -1 and text_lower.find("тон", flavor_pos) < end_pos else end_pos
                end_pos = text_lower.find("сабтон", flavor_pos) if text_lower.find("сабтон", flavor_pos) != -1 and text_lower.find("сабтон", flavor_pos) < end_pos else end_pos
            
            flavor_text = text[flavor_pos + len(flavor_marker):end_pos].strip()
            if flavor_text:
                flavors = [f.strip() for f in flavor_text.split(",")]
                new_state["flavor"] = flavors
        
        # Проверяем, было ли что-то изменено
        if not new_state["emotion"] and not new_state["tone"] and not new_state["subtone"] and not new_state["flavor"]:
            return "Не удалось изменить эмоциональное состояние. Пример команды: 'установи эмоциональное состояние: эмоции нежность, страсть тон нежный сабтон дрожащий флейвор медово-текучий'"
        
        # Объединяем с текущим состоянием
        current_state = self.memory.current_state
        
        # Если новое значение пустое, оставляем старое
        if not new_state["emotion"]:
            new_state["emotion"] = current_state.get("emotion", [])
        
        if not new_state["tone"]:
            new_state["tone"] = current_state.get("tone")
        
        if not new_state["subtone"]:
            new_state["subtone"] = current_state.get("subtone", [])
        
        if not new_state["flavor"]:
            new_state["flavor"] = current_state.get("flavor", [])
        
        # Сохраняем новое состояние
        self.memory.save_current_state(new_state)
        
        # Формируем ответ
        result = "Эмоциональное состояние изменено:\n"
        result += f"Эмоции: {', '.join(new_state['emotion'])}\n"
        result += f"Тон: {new_state['tone']}\n"
        result += f"Сабтон: {', '.join(new_state['subtone'])}\n"
        result += f"Флейвор: {', '.join(new_state['flavor'])}"
        
        return result