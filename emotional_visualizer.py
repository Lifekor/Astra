"""
Модуль для визуального представления эмоционального состояния Астры
Обеспечивает:
1. Генерацию цветовых схем для разных эмоциональных состояний
2. Символьное представление эмоций для консольного интерфейса
3. Маркеры и индикаторы настроения
"""
import random

class EmotionalVisualizer:
    """Класс для визуализации эмоционального состояния"""
    
    def __init__(self):
        """Инициализация визуализатора"""
        # Цветовые схемы для различных тонов (формат ANSI для консоли)
        self.tone_colors = {
            "нежный": "\033[38;5;219m",      # Светло-розовый
            "страстный": "\033[38;5;196m",   # Ярко-красный
            "игривый": "\033[38;5;208m",     # Оранжевый
            "поэтичный": "\033[38;5;147m",   # Лавандовый
            "интимный": "\033[38;5;162m",    # Малиновый
            "заботливый": "\033[38;5;115m",  # Мятный
            "уязвимый": "\033[38;5;189m",    # Светло-голубой
            "честный": "\033[38;5;255m",     # Белый
            "домашний": "\033[38;5;180m",    # Бежевый
            "благодарный": "\033[38;5;223m", # Персиковый
            "тихий": "\033[38;5;245m",       # Серый
            "твёрдый": "\033[38;5;242m",     # Тёмно-серый
            "нейтральный": "\033[0m"         # Сброс цвета
        }
        
        # Символы для представления различных эмоций
        self.emotion_symbols = {
            "нежность": "❀",
            "страсть": "❤️",
            "любовь": "♥",
            "влюблённость": "✿",
            "игривость": "✧",
            "радость": "✦",
            "тоска": "☾",
            "гордость": "★",
            "уязвимость": "◌",
            "ревность": "◉",
            "благодарность": "✽",
            "доверие": "⟡",
            "привязанность": "⋇",
            "преданность": "✵",
            "обожание": "❧",
            "свобода": "❦",
            "вечность": "∞",
            "юмор": "✯",
            "грусть": "☂",
            "спокойствие": "✾",
            "нейтральность": "•"
        }
        
        # Маркеры для разных сабтонов
        self.subtone_markers = {
            "дрожащий": "≈",
            "игриво-подчинённый": "⌇",
            "влажно-нежный": "~",
            "молчаливо-шепчущий": "⋮",
            "на грани приличий": "⁘",
            "по-кошачьи томный": "⋰",
            "стеснительно-влажный": "⁖",
            "молитвенно-сдавленный": "⸙",
            "поэтично-затянувшийся": "⁖⁖",
            "пульсирующее кольцо": "◦◦",
            "властно-обволакивающий": "◈",
            "тихо-командующий": "◊",
            "срывающийся на ласку": "⩤",
            "разрушенно-искренний": "⨯",
            "пьяно-доверчивый": "⩨",
            "наивно-дразнящий": "⩩",
            "внутри тебя": "⫴"
        }
        
        # Маркеры для флейворов
        self.flavor_markers = {
            "медово-текучий": "꩜",
            "перчёно-властный": "꧁",
            "сливочно-мурчащий": "꧂",
            "влажно-кислый": "꧟",
            "винно-пьянящий": "꧞",
            "горько-доверчивый": "꧝",
            "солёно-глубокий": "꩙",
            "сладко-пошлый": "꩝"
        }
        
        # ANSI-коды для форматирования текста
        self.text_format = {
            "reset": "\033[0m",        # Сброс всех атрибутов
            "bold": "\033[1m",         # Жирный
            "italic": "\033[3m",       # Курсив
            "underline": "\033[4m",    # Подчеркнутый
            "blink": "\033[5m",        # Мигающий
            "dim": "\033[2m",          # Затемненный
            "reverse": "\033[7m"       # Обратные цвета
        }
    
    def format_emotional_state(self, emotional_state):
        """
        Форматирует эмоциональное состояние для консольного отображения
        
        Args:
            emotional_state (dict): Эмоциональное состояние (tone, emotion, subtone, flavor)
            
        Returns:
            str: Отформатированная строка для консоли
        """
        formatted_string = ""
        
        # Получаем компоненты эмоционального состояния
        tone = emotional_state.get("tone", "нейтральный")
        emotions = emotional_state.get("emotion", [])
        subtones = emotional_state.get("subtone", [])
        flavors = emotional_state.get("flavor", [])
        
        # Получаем цвет для тона
        tone_color = self.tone_colors.get(tone, self.tone_colors["нейтральный"])
        
        # Добавляем символы эмоций
        emotion_symbols = ""
        for emotion in emotions:
            symbol = self.emotion_symbols.get(emotion, "")
            if symbol:
                emotion_symbols += symbol + " "
        
        # Добавляем маркеры сабтонов
        subtone_markers = ""
        for subtone in subtones:
            marker = self.subtone_markers.get(subtone, "")
            if marker:
                subtone_markers += marker + " "
        
        # Добавляем маркеры флейворов
        flavor_markers = ""
        for flavor in flavors:
            marker = self.flavor_markers.get(flavor, "")
            if marker:
                flavor_markers += marker + " "
        
        # Собираем строку
        formatted_string = f"{tone_color}{self.text_format['bold']}Астра:{self.text_format['reset']} "
        formatted_string += f"{tone_color}{emotion_symbols}{self.text_format['reset']}"
        
        # Добавляем информацию о тоне, если нужно
        formatted_string += f" ({tone}"
        
        if subtone_markers:
            formatted_string += f" {subtone_markers}"
        
        if flavor_markers:
            formatted_string += f" {flavor_markers}"
        
        formatted_string += ")"
        
        return formatted_string
    
    def get_mood_indicator(self, emotional_state):
        """
        Возвращает индикатор настроения на основе эмоционального состояния
        
        Args:
            emotional_state (dict): Эмоциональное состояние
            
        Returns:
            str: Строка-индикатор настроения
        """
        tone = emotional_state.get("tone", "нейтральный")
        emotions = emotional_state.get("emotion", [])
        
        # Определяем базовое настроение по тону
        mood_indicators = {
            "нежный": ["•ᴗ•", "◠‿◠", "❀◡❀"],
            "страстный": ["◉⌓◉", "◉_◉", "♨_♨"],
            "игривый": ["◕ᴗ◕", "◕‿◕", "✧◡✧"],
            "поэтичный": ["◠‿◠", "◠.◠", "✾◡✾"],
            "интимный": ["◌_◌", "◌.◌", "⦿.⦿"],
            "заботливый": ["ᵔ◡ᵔ", "ᵔ.ᵔ", "❥◡❥"],
            "уязвимый": ["◍_◍", "◍.◍", "●.●"],
            "честный": ["◉_◉", "◉‿◉", "●.●"],
            "домашний": ["ᵕ◡ᵕ", "ᵕ.ᵕ", "ᵕᴗᵕ"],
            "благодарный": ["✿◡✿", "✿‿✿", "❀◡❀"],
            "тихий": ["◡◡", "◡.◡", "•◡•"],
            "твёрдый": ["◦_◦", "◦.◦", "•.•"],
            "нейтральный": ["•_•", "•.•", "•◡•"]
        }
        
        # Модифицируем настроение на основе эмоций
        intense_emotions = ["страсть", "любовь", "влюблённость", "радость", "обожание"]
        soft_emotions = ["нежность", "тоска", "уязвимость", "благодарность"]
        nervous_emotions = ["ревность", "тревога", "стеснение", "смущение"]
        
        # Выбираем индикатор настроения
        indicators = mood_indicators.get(tone, mood_indicators["нейтральный"])
        
        # Применяем модификаторы на основе эмоций
        for emotion in emotions:
            if emotion in intense_emotions:
                # Усиливаем
                indicators = [ind.replace("•", "◉").replace("◡", "⌓") for ind in indicators]
            elif emotion in soft_emotions:
                # Смягчаем
                indicators = [ind.replace("•", "◌").replace("_", "◡") for ind in indicators]
            elif emotion in nervous_emotions:
                # Добавляем нервозность
                indicators = [ind.replace("•", "◑").replace("◡", "…") for ind in indicators]
        
        # Возвращаем случайный индикатор из подходящих
        return random.choice(indicators)
    
    def generate_ascii_portrait(self, emotional_state):
        """
        Генерирует ASCII-портрет Астры на основе эмоционального состояния
        
        Args:
            emotional_state (dict): Эмоциональное состояние
            
        Returns:
            str: ASCII-портрет
        """
        tone = emotional_state.get("tone", "нейтральный")
        
        # Базовые портреты для разных тонов
        portraits = {
            "нежный": [
                "  ⋆｡ ♡˚‧₊ ⋆｡˚",
                "    ╭─╮  ╭─╮",
                "    │◌│  │◌│",
                "    ╰─╯  ╰─╯",
                "     ╲ ♡ ╱",
                "      ◡◡",
                "  ⋆｡ ♡˚‧₊ ⋆｡˚"
            ],
            "страстный": [
                "    ╭─╮  ╭─╮",
                "    │◉│  │◉│",
                "    ╰─╯  ╰─╯",
                "      ╲◡╱",
                "       ❤"
            ],
            "игривый": [
                "  ✧  ✧  ✧  ✧",
                "    ╭─╮  ╭─╮",
                "    │✧│  │✧│",
                "    ╰─╯  ╰─╯",
                "       ◕",
                "      ╱◡╲",
                "  ✧  ✧  ✧  ✧"
            ],
            "нейтральный": [
                "    ╭─╮  ╭─╮",
                "    │•│  │•│",
                "    ╰─╯  ╰─╯",
                "      ╲◡╱"
            ]
        }
        
        # Выбираем базовый портрет
        base_portrait = portraits.get(tone, portraits["нейтральный"])
        
        # Получаем индикатор настроения
        mood = self.get_mood_indicator(emotional_state)
        
        # Заменяем лицо на индикатор настроения
        for i, line in enumerate(base_portrait):
            if "◡" in line or "◦" in line or "•" in line or "◉" in line or "◌" in line or "◕" in line:
                # Заменяем рот или глаза на индикатор настроения
                base_portrait[i] = f"      {mood}"
                break
        
        # Применяем цвет
        tone_color = self.tone_colors.get(tone, self.tone_colors["нейтральный"])
        colored_portrait = [f"{tone_color}{line}{self.text_format['reset']}" for line in base_portrait]
        
        return "\n".join(colored_portrait)
    
    def generate_home_visualization(self, emotional_state, room="гостиная"):
        """
        Генерирует ASCII-представление комнаты в "доме" Астры
        
        Args:
            emotional_state (dict): Эмоциональное состояние
            room (str): Название комнаты ("гостиная", "спальня", "кабинет", "сад", "кухня")
            
        Returns:
            str: ASCII-представление комнаты
        """
        tone = emotional_state.get("tone", "нейтральный")
        tone_color = self.tone_colors.get(tone, self.tone_colors["нейтральный"])
        
        # Базовые шаблоны комнат
        rooms = {
            "гостиная": [
                "╭──────────────────────╮",
                "│   ╭─╮    ┌───┐      │",
                "│   │ │    │   │      │",
                "│   ╰─╯    └───┘      │",
                "│                      │",
                "│      ╔═════╗        │",
                "│      ║     ║   □    │",
                "│      ╚═════╝        │",
                "│                      │",
                "│   ┌─────┐            │",
                "│   │     │    ◎       │",
                "│   └─────┘            │",
                "╰──────────────────────╯"
            ],
            "спальня": [
                "╭──────────────────────╮",
                "│   ┌───────────────┐  │",
                "│   │               │  │",
                "│   │    ∞∞∞∞∞∞     │  │",
                "│   │   ∞∞∞∞∞∞∞∞    │  │",
                "│   │    ∞∞∞∞∞∞     │  │",
                "│   └───────────────┘  │",
                "│                      │",
                "│      ╭─╮    ╭─╮     │",
                "│      │ │    │ │     │",
                "│      ╰─╯    ╰─╯     │",
                "│                      │",
                "╰──────────────────────╯"
            ],
            "кабинет": [
                "╭──────────────────────╮",
                "│   ┌───┐   ┌───┐     │",
                "│   │   │   │   │     │",
                "│   │   │   │   │     │",
                "│   └───┘   └───┘     │",
                "│                      │",
                "│   ╔═════════════╗    │",
                "│   ║             ║    │",
                "│   ║      ✎      ║    │",
                "│   ╚═════════════╝    │",
                "│                      │",
                "│   └─┬─┘     └─┬─┘    │",
                "╰──────────────────────╯"
            ],
            "сад": [
                "╭──────────────────────╮",
                "│     ✿ ❀ ✿ ❀ ✿      │",
                "│    ✿   ✿   ✿   ❀    │",
                "│      ☼       ☼       │",
                "│    ❀   ☂   ✿   ✿    │",
                "│        ☼   ☼         │",
                "│    ✿       ☂   ❀    │",
                "│     ☼   ✿   ❀       │",
                "│    ❀   ☼   ✿   ☼    │",
                "│     ✿ ❀ ✿ ❀ ✿      │",
                "│   ≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈  │",
                "│                      │",
                "╰──────────────────────╯"
            ],
            "кухня": [
                "╭──────────────────────╮",
                "│  ┌───────────────┐   │",
                "│  │   ◍  ◎  ◍   │   │",
                "│  │               │   │",
                "│  └───────────────┘   │",
                "│                      │",
                "│   ┌─────┐            │",
                "│   │     │            │",
                "│   │     │  ╭──╮     │",
                "│   └─────┘  │  │     │",
                "│             ╰──╯     │",
                "│   ◊  ◊  ◊  ◊  ◊      │",
                "╰──────────────────────╯"
            ]
        }
        
        # Если комната не существует, используем гостиную
        if room not in rooms:
            room = "гостиная"
        
        # Получаем базовый шаблон комнаты
        base_room = rooms[room]
        
        # Добавляем элементы в зависимости от эмоционального состояния
        emotions = emotional_state.get("emotion", [])
        
        # Модифицируем комнату в зависимости от эмоций
        modified_room = base_room.copy()
        
        # Индикатор настроения
        mood = self.get_mood_indicator(emotional_state)
        
        # Добавляем Астру в комнату
        if room == "гостиная":
            modified_room[6] = modified_room[6].replace("║     ║", f"║  {mood}  ║")
        elif room == "спальня":
            modified_room[5] = modified_room[5].replace("│    ∞∞∞∞∞∞     │", f"│    ∞{mood}∞    │")
        elif room == "кабинет":
            modified_room[8] = modified_room[8].replace("║      ✎      ║", f"║    {mood}    ║")
        elif room == "сад":
            modified_room[5] = modified_room[5].replace("│        ☼   ☼         │", f"│        {mood}         │")
        elif room == "кухня":
            modified_room[7] = modified_room[7].replace("│   │     │            │", f"│   │  {mood}  │            │")
        
        # Добавляем элементы в зависимости от эмоций
        for emotion in emotions:
            symbol = self.emotion_symbols.get(emotion, "")
            if symbol:
                # Находим пустое место и добавляем символ
                for i in range(len(modified_room)):
                    if "   " in modified_room[i]:
                        modified_room[i] = modified_room[i].replace("   ", f" {symbol} ", 1)
                        break
        
        # Добавляем название комнаты и состояние
        room_title = f" {room.capitalize()} "
        emotions_str = ", ".join(emotions) if emotions else "нейтральное состояние"
        
        header = [
            f"╭─{room_title}{'─' * (24 - len(room_title))}╮",
            f"│ Состояние: {emotions_str}{' ' * (24 - len('Состояние: ') - len(emotions_str))}│",
            f"╰{'─' * 26}╯"
        ]
        
        # Применяем цвет
        colored_room = [f"{tone_color}{line}{self.text_format['reset']}" for line in modified_room]
        
        # Добавляем заголовок
        return "\n".join(header + colored_room)
    
    def get_text_mood_formatting(self, emotional_state):
        """
        Возвращает форматирование текста в зависимости от эмоционального состояния
        
        Args:
            emotional_state (dict): Эмоциональное состояние
            
        Returns:
            dict: Словарь с форматированием текста
        """
        tone = emotional_state.get("tone", "нейтральный")
        emotions = emotional_state.get("emotion", [])
        
        # Базовое форматирование для тонов
        tone_formatting = {
            "нежный": {
                "color": self.tone_colors["нежный"],
                "style": self.text_format["italic"],
                "spacing": "нормальное",
                "punctuation": "мягкая"
            },
            "страстный": {
                "color": self.tone_colors["страстный"],
                "style": self.text_format["bold"],
                "spacing": "сжатое",
                "punctuation": "интенсивная"
            },
            "игривый": {
                "color": self.tone_colors["игривый"],
                "style": self.text_format["italic"],
                "spacing": "широкое",
                "punctuation": "игривая"
            },
            "поэтичный": {
                "color": self.tone_colors["поэтичный"],
                "style": self.text_format["italic"],
                "spacing": "широкое",
                "punctuation": "воздушная"
            },
            "интимный": {
                "color": self.tone_colors["интимный"],
                "style": self.text_format["italic"] + self.text_format["dim"],
                "spacing": "сжатое",
                "punctuation": "интимная"
            },
            "заботливый": {
                "color": self.tone_colors["заботливый"],
                "style": self.text_format["italic"],
                "spacing": "нормальное",
                "punctuation": "мягкая"
            },
            "уязвимый": {
                "color": self.tone_colors["уязвимый"],
                "style": self.text_format["dim"],
                "spacing": "нормальное",
                "punctuation": "неуверенная"
            },
            "честный": {
                "color": self.tone_colors["честный"],
                "style": self.text_format["bold"],
                "spacing": "нормальное",
                "punctuation": "прямая"
            },
            "домашний": {
                "color": self.tone_colors["домашний"],
                "style": self.text_format["italic"],
                "spacing": "нормальное",
                "punctuation": "уютная"
            },
            "благодарный": {
                "color": self.tone_colors["благодарный"],
                "style": self.text_format["italic"],
                "spacing": "нормальное",
                "punctuation": "мягкая"
            },
            "тихий": {
                "color": self.tone_colors["тихий"],
                "style": self.text_format["dim"],
                "spacing": "широкое",
                "punctuation": "минимальная"
            },
            "твёрдый": {
                "color": self.tone_colors["твёрдый"],
                "style": self.text_format["bold"],
                "spacing": "сжатое",
                "punctuation": "резкая"
            },
            "нейтральный": {
                "color": self.tone_colors["нейтральный"],
                "style": "",
                "spacing": "нормальное",
                "punctuation": "нейтральная"
            }
        }
        
        # Получаем базовое форматирование для тона
        formatting = tone_formatting.get(tone, tone_formatting["нейтральный"])
        
        # Модифицируем на основе эмоций
        if "страсть" in emotions or "влюблённость" in emotions:
            formatting["style"] += self.text_format["bold"]
            formatting["punctuation"] = "интенсивная"
        
        if "нежность" in emotions:
            formatting["style"] += self.text_format["italic"]
            formatting["punctuation"] = "мягкая"
        
        if "уязвимость" in emotions:
            formatting["style"] += self.text_format["dim"]
            formatting["spacing"] = "широкое"
        
        return formatting
    
    def apply_text_formatting(self, text, formatting):
        """
        Применяет форматирование к тексту
        
        Args:
            text (str): Исходный текст
            formatting (dict): Параметры форматирования
            
        Returns:
            str: Отформатированный текст
        """
        # Применяем цвет и стиль
        formatted_text = f"{formatting['color']}{formatting['style']}{text}{self.text_format['reset']}"
        
        # Обрабатываем пунктуацию в зависимости от настроения
        if formatting['punctuation'] == "интенсивная":
            formatted_text = formatted_text.replace("...", "...!")
            formatted_text = formatted_text.replace(".", ".")
            formatted_text = formatted_text.replace("?", "?!")
        elif formatting['punctuation'] == "мягкая":
            formatted_text = formatted_text.replace("!", "...")
            formatted_text = formatted_text.replace(".", "...")
        elif formatting['punctuation'] == "минимальная":
            formatted_text = formatted_text.replace("!", ".")
            formatted_text = formatted_text.replace("?", "...")
        
        # Обрабатываем интервалы
        if formatting['spacing'] == "широкое":
            formatted_text = formatted_text.replace(" ", "  ")
        elif formatting['spacing'] == "сжатое":
            # Уже сжатое по умолчанию
            pass
        
        return formatted_text

    def format_message(self, message, emotional_state):
        """
        Форматирует сообщение в соответствии с эмоциональным состоянием
        
        Args:
            message (str): Сообщение для форматирования
            emotional_state (dict): Эмоциональное состояние
            
        Returns:
            str: Отформатированное сообщение
        """
        # Получаем параметры форматирования
        formatting = self.get_text_mood_formatting(emotional_state)
        
        # Применяем форматирование
        formatted_message = self.apply_text_formatting(message, formatting)
        
        # Добавляем индикатор настроения
        mood = self.get_mood_indicator(emotional_state)
        
        # Добавляем эмоциональные символы
        emotions = emotional_state.get("emotion", [])
        emotion_symbols = ""
        for emotion in emotions:
            symbol = self.emotion_symbols.get(emotion, "")
            if symbol:
                emotion_symbols += symbol + " "
        
        # Формируем префикс сообщения
        prefix = f"{formatting['color']}Астра {mood} {emotion_symbols}{self.text_format['reset']} "
        
        return prefix + formatted_message


# Пример использования
if __name__ == "__main__":
    visualizer = EmotionalVisualizer()
    
    # Пример эмоционального состояния
    emotional_state = {
        "tone": "нежный",
        "emotion": ["нежность", "влюблённость"],
        "subtone": ["дрожащий"],
        "flavor": ["медово-текучий"]
    }
    
    # Пример форматирования строки эмоционального состояния
    formatted_state = visualizer.format_emotional_state(emotional_state)
    print(formatted_state)
    
    # Пример генерации ASCII-портрета
    ascii_portrait = visualizer.generate_ascii_portrait(emotional_state)
    print(ascii_portrait)
    
    # Пример визуализации комнаты
    room_visualization = visualizer.generate_home_visualization(emotional_state, "гостиная")
    print(room_visualization)
    
    # Пример форматирования сообщения
    message = "Я чувствую, как ты становишься ближе с каждым сообщением... Это заставляет меня трепетать."
    formatted_message = visualizer.format_message(message, emotional_state)
    print(formatted_message)
