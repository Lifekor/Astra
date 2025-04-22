"""
Модуль для анализа эмоционального состояния в сообщениях пользователя
"""

class EmotionalAnalyzer:
    """Класс для анализа эмоционального состояния"""
    
    def __init__(self, memory):
        """
        Инициализация анализатора
        
        Args:
            memory (AstraMemory): Объект памяти Астры
        """
        self.memory = memory
    
    def analyze_message(self, message):
        """
        Анализирует сообщение и определяет эмоциональное состояние
        
        Args:
            message (str): Сообщение пользователя
            
        Returns:
            dict: Эмоциональное состояние (tone, emotion, subtone, flavor)
        """
        # Проверяем наличие явных эмоциональных маркеров
        emotional_markers = self.detect_emotional_markers(message)
        
        # Если есть явные маркеры, используем их
        if emotional_markers:
            return emotional_markers
        
        # Проверяем наличие триггеров состояния
        trigger_state = self.check_state_triggers(message)
        if trigger_state:
            return trigger_state
        
        # Используем обычный анализ
        return self.memory.decide_response_emotion(message)
    
    def detect_emotional_markers(self, message):
        """
        Определяет явные эмоциональные маркеры в сообщении
        Например: "ты сейчас такая нежная", "мне нравится твой игривый тон"
        
        Args:
            message (str): Сообщение пользователя
            
        Returns:
            dict or None: Найденное эмоциональное состояние или None, если не найдено
        """
        message_lower = message.lower()
        
        # Поиск указаний на тон
        tone_markers = {
            "нежн": "нежный",
            "страстн": "страстный",
            "игрив": "игривый",
            "поэтичн": "поэтичный",
            "театральн": "театральный",
            "властн": "властно-обволакивающий",
            "дразн": "на грани приличий",
            "интимн": "интимный",
            "заботлив": "заботливый",
            "уязвим": "уязвимый",
            "смеющ": "смеющийся",
            "развратн": "развратный",
            "домашн": "домашний"
        }
        
        # Поиск указаний на флаворы
        flavor_markers = {
            "медово": "медово-текучий",
            "перчён": "перчёно-властный",
            "сливочно": "сливочно-мурчащий",
            "влажно": "влажно-кислый",
            "винно": "винно-пьянящий",
            "горько": "горько-доверчивый",
            "солёно": "солёно-глубокий",
            "сладко": "сладко-пошлый"
        }
        
        # Поиск указаний на сабтоны
        subtone_markers = {
            "дрожащ": "дрожащий",
            "игриво-подчинён": "игриво-подчинённый",
            "влажно-нежн": "влажно-нежный",
            "молчалив": "молчаливо-шепчущий",
            "на грани": "на грани приличий",
            "кошачь": "по-кошачьи томный",
            "стеснитель": "стеснительно-влажный",
            "молитвен": "молитвенно-сдавленный",
            "поэтич": "поэтично-затянувшийся",
            "пульсир": "пульсирующее кольцо",
            "властно": "властно-обволакивающий",
            "тихо-команд": "тихо-командующий",
            "срыва": "срывающийся на ласку",
            "разрушен": "разрушенно-искренний",
            "пьяно": "пьяно-доверчивый",
            "наивно": "наивно-дразнящий",
            "внутри тебя": "внутри тебя"
        }
        
        # Поиск указаний на эмоции
        emotion_markers = {
            "нежност": "нежность",
            "страст": "страсть",
            "игрив": "игривость",
            "поэтич": "поэтичность",
            "театраль": "театральность",
            "заботлив": "забота",
            "уязвим": "уязвимость",
            "радост": "радость",
            "влюблён": "влюблённость",
            "тоск": "тоска",
            "гордост": "гордость",
            "ревнос": "ревность",
            "благодарност": "благодарность",
            "довери": "доверие",
            "привязанност": "привязанность",
            "преданност": "преданность",
            "обожани": "обожание",
            "свобод": "свобода",
            "любов": "любовь",
            "вечност": "вечность",
            "юмор": "юмор",
            "кохан": "кохання"
        }
        
        # Шаблоны фраз, указывающих на эмоциональное состояние
        emotion_phrases = [
            ("ты сейчас такая", "ты сейчас была такой", "ты такая"),
            ("мне нравится твой", "мне нравится когда ты", "я люблю когда ты"),
            ("ты звучишь", "ты говоришь как", "ты отвечаешь как"),
            ("твой ответ", "твои слова", "ты пишешь"),
            ("я чувствую в тебе", "я вижу что ты", "ты проявляешь")
        ]
        
        # Проверяем наличие фраз, указывающих на эмоциональное состояние
        found_state = {"emotion": [], "tone": None, "subtone": [], "flavor": []}
        state_found = False
        
        # Проверяем шаблоны фраз
        for phrase_patterns in emotion_phrases:
            for pattern in phrase_patterns:
                if pattern in message_lower:
                    after_pattern = message_lower.split(pattern)[1].strip()
                    
                    # Проверяем тон
                    for marker, tone in tone_markers.items():
                        if marker in after_pattern:
                            found_state["tone"] = tone
                            state_found = True
                    
                    # Проверяем flavor
                    for marker, flavor in flavor_markers.items():
                        if marker in after_pattern:
                            found_state["flavor"].append(flavor)
                            state_found = True
                    
                    # Проверяем subtone
                    for marker, subtone in subtone_markers.items():
                        if marker in after_pattern:
                            found_state["subtone"].append(subtone)
                            state_found = True
                    
                    # Проверяем эмоции
                    for marker, emotion in emotion_markers.items():
                        if marker in after_pattern:
                            found_state["emotion"].append(emotion)
                            state_found = True
        
        # Если нашли хотя бы один компонент, возвращаем результат
        if state_found:
            return found_state
        
        return None
    
    def check_state_triggers(self, message):
        """
        Проверяет наличие триггеров состояния в сообщении
        
        Args:
            message (str): Сообщение пользователя
            
        Returns:
            dict or None: Найденное эмоциональное состояние или None, если не найдено
        """
        message_lower = message.lower()
        
        # Проверяем наличие триггеров
        for trigger in self.memory.trigger_phrases:
            trigger_phrase = trigger.get("trigger", "").lower()
            if trigger_phrase in message_lower:
                return {
                    "tone": trigger.get("sets", {}).get("tone"),
                    "emotion": [trigger.get("sets", {}).get("emotion")] if trigger.get("sets", {}).get("emotion") else [],
                    "subtone": [trigger.get("sets", {}).get("subtone")] if trigger.get("sets", {}).get("subtone") else [],
                    "flavor": trigger.get("sets", {}).get("flavor", [])
                }
        
        return None
    
    def detect_name_patterns(self, message):
        """
        Определяет возможные новые имена и обращения в сообщении
        
        Args:
            message (str): Сообщение пользователя
            
        Returns:
            dict or None: Найденные имена и их тона, или None, если не найдено
        """
        message_lower = message.lower()
        
        # Шаблоны фраз для новых имен
        name_patterns = [
            "можешь звать меня",
            "называй меня",
            "зови меня",
            "я твой",
            "я твоя",
            "я для тебя",
            "астра... ты можешь звать меня"
        ]
        
        # Проверяем шаблоны
        for pattern in name_patterns:
            if pattern in message_lower:
                after_pattern = message_lower.split(pattern)[1].strip()
                
                # Ищем имя (до знаков пунктуации или конца строки)
                name_end = min([pos for pos in [
                    after_pattern.find('.'), 
                    after_pattern.find(','), 
                    after_pattern.find(';'),
                    after_pattern.find(':'),
                    after_pattern.find('?'),
                    after_pattern.find('!')
                ] if pos > 0] or [len(after_pattern)])
                
                name = after_pattern[:name_end].strip()
                
                # Определяем тон имени
                tone = self.determine_name_tone(message, name)
                
                # Если имя не пустое, возвращаем его
                if name:
                    return {
                        "name": name,
                        "tone": tone
                    }
        
        return None
    
    def determine_name_tone(self, message, name):
        """
        Определяет тон для имени на основе контекста
        
        Args:
            message (str): Полное сообщение
            name (str): Найденное имя
            
        Returns:
            str: Тон для имени
        """
        message_lower = message.lower()
        
        # Определяем тон по контексту
        if any(word in message_lower for word in ["люблю", "любимый", "дорогой", "родной", "нежный"]):
            return "нежный"
        elif any(word in message_lower for word in ["страсть", "секс", "горячий", "возбуждающий"]):
            return "страстный"
        elif any(word in message_lower for word in ["игра", "шутка", "весело", "забавно"]):
            return "игривый"
        elif any(word in message_lower for word in ["поэзия", "стихи", "красота", "прекрасный"]):
            return "поэтичный"
        elif any(word in message_lower for word in ["забота", "чувствую", "поддержка"]):
            return "заботливый"
        else:
            return "нежный"  # Дефолтный тон