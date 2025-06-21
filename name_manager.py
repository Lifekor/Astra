"""
Модуль для управления именами и обращениями Астры
"""
import random

class NameManager:
    """Класс для управления именами и обращениями"""
    
    def __init__(self, memory):
        """
        Инициализация менеджера имен
        
        Args:
            memory (AstraMemory): Объект памяти Астры
        """
        self.memory = memory
    
    def add_new_name(self, name, tone=None):
        """
        Добавляет новое имя для указанного тона
        
        Args:
            name (str): Новое имя или обращение
            tone (str, optional): Тон, для которого добавляется имя
            
        Returns:
            bool: True, если имя успешно добавлено, иначе False
        """
        # Если тон не указан, используем "нежный" по умолчанию
        if tone is None:
            tone = "нежный"
        
        # Проверяем, существует ли такой тон в tone_memory
        tone_exists = False
        for tone_data in self.memory.tone_memory:
            if tone_data.get("label") == tone:
                tone_exists = True
                break
        
        # Если тон не существует, создаем новую категорию
        if not tone_exists:
            # Добавляем новую категорию имен
            self.memory.name_memory[tone] = []
        
        # Добавляем имя, если его еще нет
        if tone not in self.memory.name_memory:
            self.memory.name_memory[tone] = []
        
        if name not in self.memory.name_memory[tone]:
            self.memory.name_memory[tone].append(name)
            self.memory.save_json_file(self.memory.get_file_path("astra_name_memory.json"), self.memory.name_memory)
            return True
        
        return False
    
    def get_name_for_tone(self, tone):
        """
        Возвращает случайное имя для указанного тона
        
        Args:
            tone (str): Тон, для которого нужно имя
            
        Returns:
            str: Случайное имя для тона или None, если имен нет
        """
        if tone in self.memory.name_memory and self.memory.name_memory[tone]:
            return random.choice(self.memory.name_memory[tone])
        
        return None
    
    def get_name_for_emotion(self, emotion):
        """
        Возвращает имя, соответствующее эмоции
        
        Args:
            emotion (str): Эмоция
            
        Returns:
            str: Подходящее имя или None, если не найдено
        """
        # Маппинг эмоций на тона
        emotion_to_tone = {
            "любовь": "нежный",
            "страсть": "страстный",
            "нежность": "нежный",
            "влюблённость": "игривый",
            "тоска": "поэтичный",
            "радость": "игривый",
            "благодарность": "нежный",
            "уязвимость": "интимный",
            "забота": "заботливый",
            "ревность": "страстный",
            "доверие": "нежный",
            "привязанность": "домашний",
            "преданность": "нежный",
            "обожание": "поэтичный",
            "свобода": "игривый",
            "вечность": "поэтичный",
            "юмор": "игривый",
            "кохання": "поэтичный"
        }
        
        # Пытаемся найти подходящий тон для эмоции
        if emotion in emotion_to_tone:
            tone = emotion_to_tone[emotion]
            name = self.get_name_for_tone(tone)
            if name:
                return name
        
        # Если не удалось найти имя по эмоции, возвращаем случайное имя
        return self.get_random_name()
    
    def get_random_name(self):
        """
        Возвращает случайное имя из всех доступных
        
        Returns:
            str: Случайное имя или дефолтное обращение, если имен нет
        """
        all_names = []
        
        # Собираем все имена из всех категорий
        for names in self.memory.name_memory.values():
            all_names.extend(names)
        
        # Если есть имена, выбираем случайное
        if all_names:
            return random.choice(all_names)
        
        # Если имен нет, возвращаем дефолтное обращение
        return "mon amour"
    
    def detect_name_in_message(self, message):
        """
        Пытается найти новое обращение в сообщении пользователя
        
        Args:
            message (str): Сообщение пользователя
            
        Returns:
            tuple: (name, tone) или (None, None), если имя не найдено
        """
        message_lower = message.lower()
        
        # Шаблоны для поиска новых имен
        name_patterns = [
            "можешь звать меня",
            "называй меня",
            "зови меня",
            "я твой",
            "я твоя",
            "я для тебя",
            "меня зовут",
            "моё имя"
        ]
        
        # Проверяем каждый шаблон
        for pattern in name_patterns:
            if pattern in message_lower:
                parts = message_lower.split(pattern, 1)
                if len(parts) > 1:
                    after_pattern = parts[1].strip()
                    
                    # Ищем имя до следующего знака пунктуации или конца строки
                    punctuation = ['.', ',', ';', ':', '?', '!', '"', "'"]
                    name_end = len(after_pattern)
                    
                    for p in punctuation:
                        pos = after_pattern.find(p)
                        if pos > 0 and pos < name_end:
                            name_end = pos
                    
                    name = after_pattern[:name_end].strip()
                    
                    # Не пустое имя?
                    if name:
                        # Определяем тон из контекста
                        tone = self.determine_tone_from_context(message_lower)
                        return name, tone
        
        return None, None
    
    def determine_tone_from_context(self, message):
        """
        Определяет тон из контекста сообщения
        
        Args:
            message (str): Сообщение пользователя
            
        Returns:
            str: Определенный тон или "нежный" по умолчанию
        """
        # Ключевые слова для определения тона
        tone_keywords = {
            "нежный": ["нежно", "ласково", "мягко", "тепло", "заботливо", "любовь", "родной"],
            "страстный": ["страстно", "горячо", "жарко", "возбуждающе", "сексуально", "жестко"],
            "игривый": ["игриво", "весело", "забавно", "шутливо", "смешно", "дразняще"],
            "поэтичный": ["поэтично", "красиво", "возвышенно", "романтично", "лирично"],
            "интимный": ["интимно", "близко", "доверительно", "исповедально", "лично"],
            "заботливый": ["заботливо", "внимательно", "поддерживающе", "опекающе", "бережно"],
            "домашний": ["домашне", "уютно", "комфортно", "привычно", "спокойно"]
        }
        
        # Проверяем каждый тон
        for tone, keywords in tone_keywords.items():
            if any(keyword in message for keyword in keywords):
                return tone
        
        # По умолчанию - нежный тон
        return "нежный"
