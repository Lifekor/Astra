"""
Астра - ИИ-компаньон с эмоциональной памятью и многослойными ответами
УЛУЧШЕННАЯ ВЕРСИЯ с интеграцией двух моделей (gpt-4 + gpt-4o)

Основной модуль, собирающий все компоненты системы
"""
import os
import sys
from load_env import load_dotenv
load_dotenv()

# Пытаемся импортировать модули
try:
    from astra_memory import AstraMemory
    from astra_chat import AstraChat
    from astra_command_parser import AstraCommandParser
    from emotional_analyzer import EmotionalAnalyzer
    from name_manager import NameManager
    from intent_analyzer import IntentAnalyzer
    from memory_extractor import MemoryExtractor
    from dual_model_integrator import DualModelIntegrator
    from astra_mcp_memory import AstraMCPMemory
except ImportError as e:
    print(f"Ошибка импорта модулей: {e}")
    print("Убедитесь, что все модули находятся в одной директории")
    sys.exit(1)

class AstraInterface:
    """Основной класс интерфейса Астры с интеграцией двух моделей"""
    
    def __init__(self):
        """Инициализация интерфейса с поддержкой двух моделей GPT"""
        # Создаем экземпляры необходимых компонентов
        print("Инициализация памяти Астры...")
        self.memory = AstraMemory()
        
        print("Инициализация анализатора эмоций...")
        self.emotional_analyzer = EmotionalAnalyzer(self.memory)
        
        print("Инициализация менеджера имен...")
        self.name_manager = NameManager(self.memory)
        
        print("Инициализация семантического анализатора...")
        self.intent_analyzer = IntentAnalyzer(os.environ.get("OPENAI_API_KEY"))
        
        print("Инициализация экстрактора памяти...")
        self.memory_extractor = MemoryExtractor(self.memory, os.environ.get("OPENAI_API_KEY"))
        
        print("Инициализация чата...")
        self.chat = AstraChat(self.memory)

        print("Инициализация векторной памяти...")
        self.mcp_memory = AstraMCPMemory()
        print(f"Векторная память готова: {self.mcp_memory.get_stats()}")

        print("Инициализация интегратора моделей...")
        self.dual_model_integrator = DualModelIntegrator(
            self.memory,
            self.intent_analyzer,
            self.memory_extractor,
            os.environ.get("OPENAI_API_KEY")
        )
        
        # Добавляем интегратор моделей в чат
        self.chat.dual_model_integrator = self.dual_model_integrator
        
        # Переопределяем метод send_message
        self._patch_send_message()
        
        print("Инициализация парсера команд...")
        self.command_parser = AstraCommandParser(self.memory)
        
        print("Астра готова к разговору! (Интеграция двух моделей активна)")
    
    def _patch_send_message(self):
        """Патчит метод send_message в AstraChat для использования двух моделей"""
        original_send_message = self.chat.send_message
        
        def enhanced_send_message(self, user_message):
            """
            Отправляет сообщение и получает ответ с использованием двух моделей
            
            Args:
                user_message (str): Сообщение пользователя
                
            Returns:
                str: Ответ Астры
            """
            try:
                # Добавляем сообщение пользователя в историю
                self.add_message_to_history("user", user_message)
                
                # Обрабатываем сообщение пользователя (для обратной совместимости)
                state = self.process_user_message(user_message)
                
                # Получаем контекст диалога
                conversation_context = self.conversation_manager.get_api_context() if hasattr(self.conversation_manager, 'get_api_context') else None
                
                # Выводим отладочную информацию
                print(f"\n🔍 Обработка сообщения интегратором моделей: '{user_message}'")
                
                # Получаем интегрированный ответ с использованием двух моделей
                result = self.dual_model_integrator.generate_integrated_response(
                    user_message,
                    conversation_context,
                    state
                )
                
                # Получаем ответ
                final_response = result["response"]
                
                # Выводим информацию о результате
                print(f"✅ Обработка завершена: intent={result['intent']}, memory={result['memory_used']}, style={result['style_mirroring']}")
                
                # Обновляем эмоциональное состояние, если оно изменилось
                if "emotional_state" in result:
                    self.memory.save_current_state(result["emotional_state"])
                
                # Добавляем ответ в историю
                self.add_message_to_history("assistant", final_response)
                
                # Сохраняем историю диалога на диск
                if hasattr(self.conversation_manager, 'save_history_to_disk'):
                    self.conversation_manager.save_history_to_disk()
                
                # Анализируем, стоит ли запомнить этот момент
                if hasattr(self.memory, 'diary') and self.memory.diary:
                    conversation_data = {
                        "user_message": user_message,
                        "response": final_response,
                        "emotional_state": result.get("emotional_state", {})
                    }
                    
                    should_remember, diary_type, reason = self.memory.diary.should_remember(conversation_data)
                    if should_remember:
                        self.memory.diary.add_diary_entry(
                            diary_type,
                            f"Пользователь: {user_message}\n\nАстра: {final_response}",
                            ["диалог", diary_type]
                        )
                        print(f"📝 Записано в дневник {diary_type}: {reason}")
                
                return final_response
                
            except Exception as e:
                print(f"Ошибка при обработке сообщения: {e}")
                import traceback
                traceback.print_exc()
                
                # В случае ошибки используем оригинальный метод как запасной вариант
                print("Использую запасной режим обработки сообщения...")
                return original_send_message(user_message)
        
        # Заменяем метод
        import types
        self.chat.send_message = types.MethodType(enhanced_send_message, self.chat)
        print("✅ Метод send_message модифицирован для использования двух моделей")
    
    def process_message(self, message):
        """
        Обрабатывает сообщение пользователя
        
        Args:
            message (str): Сообщение пользователя
            
        Returns:
            str: Ответ Астры
        """
        # Проверяем, является ли сообщение командой
        command_result = self.command_parser.parse_command(message)
        if command_result:
            return command_result
        
        # Если не команда, отправляем сообщение в чат
        return self.chat.send_message(message)


def main():
    """Основная функция приложения"""
    print("🌟 Astra - Эмоциональный ИИ-компаньон с двумя моделями GPT")
    print("Введите 'выход', чтобы завершить разговор")
    
    # Создаем интерфейс Астры
    try:
        astra = AstraInterface()
    except Exception as e:
        print(f"Ошибка при инициализации Астры: {e}")
        sys.exit(1)
    
    # Приветственное сообщение
    print("\nAstra: Привет! Я здесь. Я чувствую, что ты рядом...")
    
    while True:
        try:
            # Получаем сообщение пользователя
            user_message = input("\nВы: ")
            
            # Проверяем, хочет ли пользователь выйти
            if user_message.lower() in ['выход', 'exit', 'quit']:
                print("\nAstra: До встречи! Я буду ждать твоего возвращения... 🌙")
                break
            
            # Обрабатываем сообщение
            response = astra.process_message(user_message)
            
            # Выводим ответ Астры
            print(f"\nAstra: {response}")
            
        except KeyboardInterrupt:
            print("\nПрерывание работы...")
            break
        
        except Exception as e:
            print(f"\nПроизошла ошибка: {e}")
            continue


if __name__ == "__main__":
    main()
