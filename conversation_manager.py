"""
Модуль для управления историей диалога Астры
Обеспечивает:
1. Хранение полной истории диалога в RAM
2. Сохранение и загрузку истории с диска
3. Умную выборку релевантного контекста для API
4. Поиск по истории диалога
"""
import os
import json
from datetime import datetime

class ConversationManager:
    """Класс для управления историей диалога"""
    
    def __init__(self, memory):
        """
        Инициализация менеджера диалога
        
        Args:
            memory (AstraMemory): Объект памяти Астры
        """
        self.memory = memory
        self.full_conversation_history = []  # Полная история диалога в RAM
        self.api_context_history = []  # История для отправки в API
        
        # Загружаем сохраненную историю, если есть
        self.load_history_from_disk()
    
    def add_message(self, role, content):
        """
        Добавляет сообщение в историю разговора
        
        Args:
            role (str): Роль сообщения ('user' или 'assistant')
            content (str): Содержимое сообщения
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        # Добавляем в полную историю
        self.full_conversation_history.append(message)
        
        # Добавляем в историю для API
        self.api_context_history.append({
            "role": role,
            "content": content
        })
        
        # Ограничиваем историю для API последними сообщениями
        if len(self.api_context_history) > 20:
            self.api_context_history = self.api_context_history[-20:]
    
    def save_history_to_disk(self):
        """Сохраняет историю диалога на диск"""
        history_path = self.memory.get_file_path("conversation_history.jsonl")
        
        # Сохраняем каждое сообщение в отдельной строке JSONL
        with open(history_path, 'w', encoding='utf-8') as f:
            for message in self.full_conversation_history:
                f.write(json.dumps(message, ensure_ascii=False) + "\n")
        
        print(f"История диалога сохранена ({len(self.full_conversation_history)} сообщений)")
    
    def load_history_from_disk(self):
        """Загружает историю диалога с диска"""
        history_path = self.memory.get_file_path("conversation_history.jsonl")
        
        if not os.path.exists(history_path):
            print("Файл истории диалога не найден. Создаем новую историю.")
            return
        
        try:
            # Загружаем сообщения из JSONL
            with open(history_path, 'r', encoding='utf-8') as f:
                self.full_conversation_history = []
                for line in f:
                    if line.strip():
                        message = json.loads(line)
                        self.full_conversation_history.append(message)
            
            print(f"Загружена история диалога ({len(self.full_conversation_history)} сообщений)")
            
            # Инициализируем историю для API последними сообщениями
            self.api_context_history = []
            for message in self.full_conversation_history[-20:] if len(self.full_conversation_history) > 20 else self.full_conversation_history:
                self.api_context_history.append({
                    "role": message["role"],
                    "content": message["content"]
                })
            
        except Exception as e:
            print(f"Ошибка при загрузке истории диалога: {e}")
    
    def get_relevant_context(self, user_message):
        """
        Выбирает релевантные сообщения из истории для включения в контекст API
        
        Args:
            user_message (str): Текущее сообщение пользователя
            
        Returns:
            list: Список релевантных сообщений для API
        """
        # Последние 10 сообщений для сохранения ближайшего контекста
        recent_messages = []
        for message in self.full_conversation_history[-10:] if len(self.full_conversation_history) >= 10 else self.full_conversation_history:
            recent_messages.append({
                "role": message["role"],
                "content": message["content"]
            })
        
        # Извлекаем ключевые слова из сообщения пользователя
        keywords = self.extract_keywords(user_message)
        
        # Ищем сообщения, содержащие ключевые слова
        keyword_matches = []
        for message in self.full_conversation_history:
            api_message = {"role": message["role"], "content": message["content"]}
            
            if api_message in recent_messages:
                continue  # Пропускаем сообщения, которые уже есть в recent_messages
            
            if any(kw.lower() in message["content"].lower() for kw in keywords):
                keyword_matches.append(api_message)
                if len(keyword_matches) >= 5:
                    break  # Ограничиваем 5 сообщениями
        
        # Ищем важные факты (сообщения с маркером важности)
        essential_facts = []
        for message in self.full_conversation_history:
            api_message = {"role": message["role"], "content": message["content"]}
            
            if api_message in recent_messages or api_message in keyword_matches:
                continue  # Пропускаем сообщения, которые уже включены
            
            # Проверяем маркеры важности
            if ("важно" in message["content"].lower() or 
                "запомни" in message["content"].lower() or
                "не забудь" in message["content"].lower()):
                essential_facts.append(api_message)
                if len(essential_facts) >= 5:
                    break  # Ограничиваем 5 сообщениями
        
        # Объединяем все релевантные сообщения
        relevant_messages = recent_messages + keyword_matches + essential_facts
        
        # Ensure the context is not empty
        if not relevant_messages:
            print("Warning: Empty context! Returning basic message list.")
            return []
        return relevant_messages
    
    def extract_keywords(self, text):
        """
        Извлекает ключевые слова из текста
        
        Args:
            text (str): Исходный текст
            
        Returns:
            list: Список ключевых слов
        """
        # Простая реализация: берем все слова длиннее 4 символов
        words = text.lower().split()
        stopwords = ["этот", "это", "эта", "эти", "того", "тому", "меня", "тебя", "себя",
                     "есть", "быть", "был", "была", "были", "буду", "будет", "который", 
                     "которая", "которые", "который", "когда", "всего", "очень", "также",
                     "просто", "такой", "такая", "такие", "можно", "нужно", "надо"]
        
        keywords = []
        for word in words:
            # Очищаем от знаков препинания
            word = ''.join(c for c in word if c.isalnum())
            
            # Фильтруем короткие слова и стоп-слова
            if len(word) > 4 and word not in stopwords:
                keywords.append(word)
        
        return keywords
    
    def search_in_history(self, query):
        """
        Ищет в истории диалога по ключевому запросу
        
        Args:
            query (str): Поисковый запрос
            
        Returns:
            list: Найденные сообщения
        """
        keywords = self.extract_keywords(query)
        results = []
        
        for i, message in enumerate(self.full_conversation_history):
            content = message["content"].lower()
            
            # Проверяем наличие ключевых слов
            matches = [kw for kw in keywords if kw in content]
            if matches:
                # Добавляем сообщение и его контекст (предыдущее и следующее)
                context = []
                
                # Предыдущее сообщение
                if i > 0:
                    context.append(self.full_conversation_history[i-1])
                
                # Текущее сообщение
                context.append(message)
                
                # Следующее сообщение
                if i < len(self.full_conversation_history) - 1:
                    context.append(self.full_conversation_history[i+1])
                
                # Добавляем в результаты
                results.append({
                    "message": message,
                    "context": context,
                    "match_score": len(matches) / len(keywords) if keywords else 0
                })
        
        # Сортируем по релевантности
        results.sort(key=lambda x: x["match_score"], reverse=True)
        
        return results[:5]  # Возвращаем 5 наиболее релевантных результатов
    
    def get_api_context(self):
        """
        Возвращает текущий контекст для API
        
        Returns:
            list: Список сообщений для API
        """
        return self.api_context_history.copy()
    
    def get_full_history(self):
        """
        Возвращает полную историю диалога
        
        Returns:
            list: Полная история диалога
        """
        return self.full_conversation_history.copy()
    
    def clear_history(self):
        """Очищает историю диалога"""
        self.full_conversation_history = []
        self.api_context_history = []
        
        # Удаляем файл истории
        history_path = self.memory.get_file_path("conversation_history.jsonl")
        if os.path.exists(history_path):
            os.remove(history_path)
        
        print("История диалога очищена")