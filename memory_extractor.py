"""
Модуль для извлечения релевантных воспоминаний Астры на основе контекста
"""
import os
import glob
import json
from datetime import datetime
from intent_analyzer import IntentAnalyzer
from astra_mcp_memory import AstraMCPMemory

try:
    import tiktoken  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    tiktoken = None


def _count_tokens(text: str) -> int:
    """Approximate token count for a text fragment."""
    if tiktoken:
        enc = tiktoken.encoding_for_model("gpt-4o")
        return len(enc.encode(text))
    return len(text) // 4

class MemoryExtractor:
    """Класс для извлечения релевантных воспоминаний"""
    
    def __init__(self, memory, api_key=None):
        """
        Инициализация экстрактора памяти
        
        Args:
            memory (AstraMemory): Объект памяти Астры
            api_key (str, optional): API ключ для запросов к OpenAI
        """
        self.memory = memory
        self.intent_analyzer = IntentAnalyzer(api_key)
        # Semantic memory backed by FAISS (falls back if dependencies missing)
        self.mcp_memory = AstraMCPMemory(data_dir=memory.get_file_path(""))

        # Debug log for tracing memory search steps
        self.debug_log_file = os.path.join(
            memory.get_file_path(""), "memory_search.log"
        )

        # Кэш загруженных дневников
        self.diaries = {}
        
        # Загружаем дневники при инициализации
        self.load_diaries()

    def _log_debug(self, step_name: str, data) -> None:
        """Append debug information to the memory search log."""
        try:
            entry = f"[{datetime.now().isoformat()}] {step_name}\n"
            if isinstance(data, (dict, list)):
                entry += json.dumps(data, ensure_ascii=False, indent=2)
            else:
                entry += str(data)
            entry += "\n" + "-" * 80 + "\n"
            with open(self.debug_log_file, "a", encoding="utf-8") as f:
                f.write(entry)
        except Exception:
            pass
    
    def load_diaries(self):
        """Загружает все дневники из директории данных"""
        diary_path = self.memory.get_file_path("")  # Получаем базовый путь к директории данных
        
        # Ищем все .txt файлы в директории данных
        diary_files = glob.glob(os.path.join(diary_path, "*.txt"))
        
        # Загружаем каждый дневник
        for file_path in diary_files:
            diary_name = os.path.basename(file_path).replace(".txt", "")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    diary_content = f.read()
                
                self.diaries[diary_name] = diary_content
                print(f"Загружен дневник: {diary_name}")
            except Exception as e:
                print(f"Ошибка при загрузке дневника {diary_name}: {e}")
    
    def get_memory_fragments(self, diary_name, chunk_size=300, overlap=50):
        """
        Разбивает дневник на фрагменты для анализа
        
        Args:
            diary_name (str): Имя дневника
            chunk_size (int): Размер фрагмента в символах
            overlap (int): Размер перекрытия фрагментов
            
        Returns:
            list: Список фрагментов дневника
        """
        if diary_name not in self.diaries:
            return []
        
        diary_content = self.diaries[diary_name]
        
        # Разбиваем дневник на отдельные абзацы
        paragraphs = diary_content.split('\n\n')
        fragments = []
        
        # Формируем фрагменты
        current_fragment = ""
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # Если добавление абзаца превышает chunk_size, сохраняем текущий фрагмент
            if len(current_fragment) + len(paragraph) > chunk_size and current_fragment:
                fragments.append(current_fragment)
                
                # Для перекрытия берем последнюю часть текущего фрагмента
                words = current_fragment.split()
                if len(words) > 10:  # Если есть достаточно слов для перекрытия
                    # Берем примерно последние overlap символов (по словам)
                    overlap_text = ""
                    for word in reversed(words):
                        if len(overlap_text) + len(word) + 1 > overlap:
                            break
                        overlap_text = word + " " + overlap_text
                    
                    current_fragment = overlap_text
                else:
                    current_fragment = ""
            
            # Добавляем абзац к текущему фрагменту
            if current_fragment:
                current_fragment += "\n\n" + paragraph
            else:
                current_fragment = paragraph
        
        # Добавляем последний фрагмент, если он не пустой
        if current_fragment:
            fragments.append(current_fragment)
        
        return fragments
    
    def extract_relevant_memories(
        self,
        user_message,
        intent_data=None,
        conversation_context=None,
        model=None,
        memory_token_limit=3000,
    ):
        """
        Извлекает релевантные воспоминания на основе намерения пользователя
        
        Args:
            user_message (str): Сообщение пользователя
            intent_data (dict, optional): Данные о намерении пользователя
            conversation_context (list, optional): Контекст диалога
            model (str, optional): Модель для поиска воспоминаний (по умолчанию выбирается автоматически)
            memory_token_limit (int, optional): Максимальное число токенов дневниковых фрагментов
                для анализа релевантности
            
        Returns:
            dict: Структура с релевантными воспоминаниями
        """
        # Если данные о намерении не переданы, получаем их
        if intent_data is None:
            intent_data = self.intent_analyzer.analyze_intent(
                user_message, conversation_context
            )
            self._log_debug("intent_analysis", intent_data)
        
        # Получаем список релевантных типов памяти
        memory_types = intent_data.get("match_memory", [])

        # Получаем тип интента
        intent = intent_data.get("intent", "")

        # Попытка семантического поиска в MCP памяти
        mcp_results = self.mcp_memory.semantic_search(user_message, top_k=5)
        if mcp_results:
            memories = [{"text": r["text"], "relevance": r["score"]} for r in mcp_results]
            sources = {r["text"]: r.get("source", "mcp") for r in mcp_results}
            return {"intent": intent, "memories": memories, "sources": sources}
        
        # Модель для релевантности памяти по умолчанию gpt-3.5-turbo
        model_to_use = model or "gpt-3.5-turbo"

        self._log_debug(
            "memory_search_start",
            {
                "user_message": user_message,
                "memory_types": memory_types,
                "model": model_to_use,
                "token_limit": memory_token_limit,
            },
        )
        
        # Если список пустой, используем базовые типы в зависимости от намерения
        if not memory_types:
            intent = intent_data.get("intent", "")
            
            if intent == "about_user":
                memory_types = ["relationship_memory", "user_preferences"]
            elif intent == "about_relationship":
                memory_types = ["relationship_memory", "astra_memories", "astra_intimacy"]
            elif intent == "about_astra":
                memory_types = ["core_memory", "astra_memories"]
            elif intent == "intimate":
                memory_types = ["astra_intimacy", "relationship_memory"]
            elif intent == "memory_recall":
                memory_types = ["astra_memories", "relationship_memory"]
            else:
                memory_types = ["astra_memories", "core_memory"]
        
        # Собираем фрагменты из всех релевантных типов памяти
        all_fragments = []
        fragments_sources = {}
        used_tokens = 0
        
        for memory_type in memory_types:
            # Преобразуем название типа памяти в имя файла
            diary_names = []
            
            if memory_type == "core_memory":
                diary_names = ["astra_core_prompt"]
            elif memory_type == "relationship_memory":
                diary_names = ["relationship_memory", "astra_memories"]
            elif memory_type == "emotion_memory":
                diary_names = ["emotion_memory", "tone_memory", "subtone_memory", "flavor_memory"]
            elif memory_type == "user_preferences":
                diary_names = ["relationship_memory", "user_preferences"]
            else:
                # Для остальных типов используем их имя как имя дневника
                diary_names = [memory_type]
            
            # Получаем фрагменты из каждого дневника
            for diary_name in diary_names:
                # Убираем расширение для поиска в self.diaries
                diary_key = diary_name.replace(".txt", "")
                
                if diary_key in self.diaries and used_tokens < memory_token_limit:
                    fragments = self.get_memory_fragments(diary_key)

                    for fragment in fragments:
                        tokens = _count_tokens(fragment)
                        if used_tokens + tokens > memory_token_limit:
                            break
                        all_fragments.append(fragment)
                        fragments_sources[fragment] = diary_name
                        used_tokens += tokens
                    if used_tokens >= memory_token_limit:
                        break
            if used_tokens >= memory_token_limit:
                break
        # Если превысили лимит токенов, прекращаем добавление

        self._log_debug(
            "fragments_collected",
            {
                "count": len(all_fragments),
                "used_tokens": used_tokens,
                "sources": list({v for v in fragments_sources.values()}),
            },
        )
        
        # Если у нас нет фрагментов, возвращаем пустой результат
        if not all_fragments:
            return {
                "intent": intent_data.get("intent", "unknown"),
                "memories": [],
                "sources": {}
            }
        
        # Определяем релевантность фрагментов используя выбранную модель
        relevance_data = self.intent_analyzer.get_semantic_relevance(
            user_message,
            all_fragments,
            model=model_to_use,
            intent=intent,
            strategy="compact_relevance",
            memory_token_limit=800,
        )
        relevant_fragments = relevance_data.get("fragments", [])
        self._log_debug("relevance_result", relevance_data)
        
        # Формируем результат
        result = {
            "intent": intent_data.get("intent", "unknown"),
            "memories": relevant_fragments,
            "sources": {},
        }

        if "_token_usage" in relevance_data:
            result["_token_usage"] = relevance_data["_token_usage"]
        
        # Добавляем источник для каждого фрагмента
        for fragment in relevant_fragments:
            text = fragment["text"]
            if text in fragments_sources:
                result["sources"][text] = fragments_sources[text]

        self._log_debug("memory_search_result", result)

        return result
