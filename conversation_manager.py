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
from typing import List

try:  # optional dependency for semantic search
    from sentence_transformers import SentenceTransformer, util  # type: ignore
except Exception:  # pragma: no cover - handle missing dependency gracefully
    SentenceTransformer = None
    util = None

class ConversationManager:
    """Класс для управления историей диалога"""
    
    def __init__(self, memory):
        """
        Инициализация менеджера диалога
        
        Args:
            memory (AstraMemory): Объект памяти Астры
        """
        self.memory = memory
        self.full_conversation_history: List[dict] = []  # Полная история диалога в RAM
        self.api_context_history: List[dict] = []  # История для отправки в API
        self.summary_history: List[dict] = []  # Сохраненные сводки
        self.latest_summary = None

        # Semantic search components
        self.embedding_model = None
        self.message_embeddings: List = []
        self._init_embedding_model()

        # Загружаем сохраненную историю и сводки, если есть
        self.load_history_from_disk()
        self.load_summaries_from_disk()

    def _init_embedding_model(self):
        """Initialize sentence transformer model if available"""
        if SentenceTransformer is None:
            print("sentence_transformers not available, semantic search disabled.")
            return
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:  # pragma: no cover - runtime dependency issues
            print(f"Failed to load embedding model: {e}")
            self.embedding_model = None
        self._rebuild_embeddings()

    def _rebuild_embeddings(self):
        """Recompute embeddings for the entire history"""
        self.message_embeddings = []
        if not self.embedding_model:
            return
        contents = [m.get("content", "") for m in self.full_conversation_history]
        if contents:
            try:
                embeddings = self.embedding_model.encode(contents, convert_to_tensor=True)
                # `encode` returns a single tensor for the batch; convert to a list
                # of tensors so new embeddings can be appended without errors.
                self.message_embeddings = [emb for emb in embeddings]
            except Exception as e:  # pragma: no cover - encoding may fail
                print(f"Failed to encode history embeddings: {e}")
                self.message_embeddings = []
    
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
        if self.embedding_model:
            try:
                emb = self.embedding_model.encode(content, convert_to_tensor=True)
                self.message_embeddings.append(emb)
            except Exception:
                self.message_embeddings.append(None)
        else:
            self.message_embeddings.append(None)
        
        # Добавляем в историю для API
        self.api_context_history.append({
            "role": role,
            "content": content
        })
        
        # Ограничиваем историю для API последними сообщениями
        if len(self.api_context_history) > 20:
            self.api_context_history = self.api_context_history[-20:]

        # Периодически создаем сводку для сохранения старых сообщений
        self.summarize_history()
    
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

            # Пересчитываем эмбеддинги для загруженной истории
            self._rebuild_embeddings()

        except Exception as e:
            print(f"Ошибка при загрузке истории диалога: {e}")

    def load_summaries_from_disk(self):
        """Загружает файл сводок диалога"""
        summaries_path = self.memory.get_file_path("conversation_summaries.jsonl")

        if not os.path.exists(summaries_path):
            print("Файл сводок диалога не найден. Создаем новый.")
            self.summary_history = []
            self.latest_summary = None
            return

        try:
            self.summary_history = []
            with open(summaries_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self.summary_history.append(json.loads(line))
            if self.summary_history:
                self.latest_summary = self.summary_history[-1].get("summary")
        except Exception as e:
            print(f"Ошибка при загрузке сводок диалога: {e}")

    def summarize_history(self, max_recent=50, summary_words=40):
        """Сохраняет краткую сводку старых сообщений, если история слишком длинная"""

        if len(self.full_conversation_history) <= max_recent:
            return None

        old_messages = self.full_conversation_history[:-max_recent]
        text = " ".join(m["content"] for m in old_messages)
        words = text.split()
        snippet = " ".join(words[:summary_words])
        if len(words) > summary_words:
            snippet += "..."

        record = {
            "timestamp": datetime.now().isoformat(),
            "summary": snippet
        }

        summaries_path = self.memory.get_file_path("conversation_summaries.jsonl")
        with open(summaries_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

        self.summary_history.append(record)
        self.latest_summary = snippet

        # Оставляем только последние сообщения в памяти
        self.full_conversation_history = self.full_conversation_history[-max_recent:]
        if len(self.api_context_history) > max_recent:
            self.api_context_history = self.api_context_history[-max_recent:]
        if self.message_embeddings:
            self.message_embeddings = self.message_embeddings[-max_recent:]

        return snippet

    def semantic_search(self, text, top_k: int = 5):
        """Return top_k semantically similar messages to the query"""
        if not self.embedding_model or not self.message_embeddings:
            return []
        try:
            query_emb = self.embedding_model.encode(text, convert_to_tensor=True)
            scores = util.cos_sim(query_emb, self.message_embeddings)[0]
            top_k = min(top_k, len(scores))
            indices = scores.topk(k=top_k).indices.tolist()
            results = []
            for idx in indices:
                msg = self.full_conversation_history[idx]
                results.append({"role": msg["role"], "content": msg["content"]})
            return results
        except Exception as e:  # pragma: no cover - runtime errors
            print(f"Semantic search failed: {e}")
            return []
    
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

        # Semantic search based on sentence embeddings
        semantic_matches = self.semantic_search(user_message)
        
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
        
        # Объединяем все релевантные сообщения, исключая дубликаты
        relevant_messages = []
        seen = set()
        for msg in recent_messages + semantic_matches + keyword_matches + essential_facts:
            key = (msg["role"], msg["content"])
            if key not in seen:
                relevant_messages.append(msg)
                seen.add(key)

        # Если были созданы сводки, добавляем последнюю как системное сообщение
        if self.latest_summary:
            summary_message = {
                "role": "system",
                "content": f"Сводка предыдущего диалога: {self.latest_summary}"
            }
            relevant_messages.insert(0, summary_message)
        
        # Ensure the context is not empty
        if not relevant_messages:
            print("Warning: Empty context! Returning basic message list.")
            return recent_messages
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
                     "которая", "которые", "когда", "всего", "очень", "также",
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
            list: Список словарей с ключами "message", "context" и "match_score"
                message (dict): найденное сообщение
                context (list): соседние сообщения, включающие предыдущее и
                    следующее
                match_score (float): степень совпадения запроса
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
        self.message_embeddings = []
        
        # Удаляем файл истории
        history_path = self.memory.get_file_path("conversation_history.jsonl")
        if os.path.exists(history_path):
            os.remove(history_path)
        
        print("История диалога очищена")
