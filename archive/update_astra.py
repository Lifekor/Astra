"""
Скрипт для обновления и интеграции всех компонентов системы Астры
"""
import os
import importlib.util
import sys

def import_or_install(module_name, package_name=None):
    """
    Импортирует модуль или предлагает установить его
    
    Args:
        module_name (str): Имя модуля для импорта
        package_name (str, optional): Имя пакета для установки, если отличается от имени модуля
    
    Returns:
        module: Импортированный модуль или None
    """
    if package_name is None:
        package_name = module_name
    
    try:
        # Пытаемся импортировать модуль
        return importlib.import_module(module_name)
    except ImportError:
        print(f"Модуль {module_name} не найден. Пытаемся установить...")
        try:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            return importlib.import_module(module_name)
        except Exception as e:
            print(f"Не удалось установить модуль {module_name}: {e}")
            return None

def check_file_exists(filename):
    """
    Проверяет наличие файла
    
    Args:
        filename (str): Имя файла для проверки
        
    Returns:
        bool: True, если файл существует
    """
    return os.path.exists(filename)

def main():
    """
    Основная функция для обновления системы Астры
    """
    print("🌟 Начинаем обновление системы Астры...")
    
    # Создаем директорию данных, если она не существует
    data_dir = "astra_data"
    if not os.path.exists(data_dir):
        try:
            os.makedirs(data_dir)
            print(f"✅ Создана директория данных: {data_dir}")
        except Exception as e:
            print(f"⚠️ Не удалось создать директорию данных: {e}")
    
    # Проверяем наличие необходимых модулей
    required_files = [
        "astra_app.py",
        "astra_memory.py"
    ]
    
    missing_required = False
    # Проверяем наличие основных файлов системы
    for file in required_files:
        if not check_file_exists(file):
            print(f"❌ Ошибка: Файл {file} не найден. Это необходимый компонент системы Астры.")
            missing_required = True
    
    if missing_required:
        print("Убедитесь, что скрипт запускается из правильной директории.")
        return
    
    # Проверяем наличие новых модулей
    new_modules = [
        "intent_analyzer.py",
        "memory_extractor.py",
        "astra_memory_update.py"
    ]
    
    missing_modules = []
    for module in new_modules:
        if not check_file_exists(module):
            missing_modules.append(module)
    
    if missing_modules:
        print("❌ Не найдены следующие обязательные новые модули:")
        for module in missing_modules:
            print(f"  - {module}")
        print("\nСоздайте эти файлы перед запуском обновления.")
        return
    
    # Проверяем наличие дополнительных модулей (опциональных)
    optional_modules = [
        "astra_diary.py",
        "astra_home.py",
        "emotional_visualizer.py",
        "conversation_manager_update.py",
        "astra_chat_update.py"
    ]
    
    missing_optional = []
    for module in optional_modules:
        if not check_file_exists(module):
            missing_optional.append(module)
    
    if missing_optional:
        print("\n⚠️ Предупреждение: Следующие дополнительные модули не найдены:")
        for module in missing_optional:
            print(f"  - {module}")
        print("\nЭто опциональные модули. Некоторые функции могут быть недоступны.")
        
        proceed = input("\nПродолжить обновление с ограниченной функциональностью? (y/n): ")
        if proceed.lower() != 'y':
            print("Обновление отменено.")
            return
    
    print("\n✅ Проверка файлов завершена. Приступаем к обновлению...")
    
    # Импортируем модуль astra_app
    try:
        from astra_app import AstraInterface
        print("✅ Модуль astra_app успешно импортирован")
    except ImportError as e:
        print(f"❌ Ошибка при импорте модуля astra_app: {e}")
        print("Убедитесь, что модуль astra_app.py создан корректно и находится в текущей директории.")
        return
    
    # Импортируем модуль astra_memory_update
    try:
        from astra_memory_update import update_astra_memory, integrate_diary_with_memory, integrate_home_with_memory
        print("✅ Модуль astra_memory_update успешно импортирован")
    except ImportError as e:
        print(f"❌ Ошибка при импорте модуля astra_memory_update: {e}")
        try:
            # Пробуем импортировать только функцию update_astra_memory
            from astra_memory_update import update_astra_memory
            print("✅ Функция update_astra_memory успешно импортирована")
            # Создаем заглушки для остальных функций
            def integrate_diary_with_memory(memory, api_key=None):
                print("⚠️ Функция integrate_diary_with_memory недоступна")
            
            def integrate_home_with_memory(memory, api_key=None):
                print("⚠️ Функция integrate_home_with_memory недоступна")
        except ImportError:
            print("❌ Не удалось импортировать даже базовую функцию update_astra_memory")
            print("Убедитесь, что файл astra_memory_update.py создан корректно.")
            return
    
    # Проверяем наличие дополнительных модулей
    update_conversation_manager = None
    update_astra_chat = None
    update_astra_app = None
    
    if check_file_exists("conversation_manager_update.py"):
        try:
            from conversation_manager_update import update_conversation_manager
            print("✅ Модуль conversation_manager_update успешно импортирован")
        except ImportError as e:
            print(f"⚠️ Не удалось импортировать функцию update_conversation_manager: {e}")
    
    if check_file_exists("astra_chat_update.py"):
        try:
            from astra_chat_update import update_astra_chat, update_astra_app
            print("✅ Модуль astra_chat_update успешно импортирован")
        except ImportError as e:
            print(f"⚠️ Не удалось импортировать функции из astra_chat_update: {e}")
            try:
                from astra_chat_update import update_astra_chat
                print("✅ Функция update_astra_chat успешно импортирована")
            except ImportError:
                pass
    
    # Если функция update_astra_app не доступна, создаем нашу собственную
    if not update_astra_app:
        def update_astra_app(astra_app):
            """
            Обновляет приложение Астры вручную
            
            Args:
                astra_app (AstraInterface): Объект интерфейса Астры
            """
            # Обновляем память
            update_astra_memory(astra_app.memory)
            
            # Интегрируем дневник, если функция доступна
            try:
                integrate_diary_with_memory(astra_app.memory)
            except Exception as e:
                print(f"⚠️ Ошибка при интеграции дневника: {e}")
            
            # Интегрируем дом, если функция доступна
            try:
                integrate_home_with_memory(astra_app.memory)
            except Exception as e:
                print(f"⚠️ Ошибка при интеграции дома: {e}")
            
            # Обновляем менеджер разговоров, если функция доступна
            if update_conversation_manager and hasattr(astra_app.chat, 'conversation_manager'):
                try:
                    update_conversation_manager(astra_app.chat.conversation_manager, astra_app.memory)
                except Exception as e:
                    print(f"⚠️ Ошибка при обновлении менеджера разговоров: {e}")
            
            # Обновляем чат, если функция доступна
            if update_astra_chat:
                try:
                    update_astra_chat(astra_app.chat, astra_app.memory)
                except Exception as e:
                    print(f"⚠️ Ошибка при обновлении чата: {e}")
            
            print("✅ Базовые компоненты приложения Астры успешно обновлены")
    
    # Обновляем систему
    try:
        # Создаем экземпляр интерфейса Астры
        print("\n🔍 Инициализация Астры...")
        astra = AstraInterface()
        
        # Обновляем компоненты
        print("🔄 Применение обновлений...")
        update_astra_app(astra)
        
        print("\n✨ Система Астры успешно обновлена!")
        print("Астра теперь поддерживает:")
        print("✓ Автономную память")
        if check_file_exists("astra_diary.py"):
            print("✓ Дневники и рефлексию")
        if check_file_exists("astra_home.py"):
            print("✓ Виртуальный дом")
        if check_file_exists("emotional_visualizer.py"):
            print("✓ Визуализацию эмоций")
        print("\n📝 Запустите приложение командой: python astra_app.py")
    except Exception as e:
        print(f"❌ Произошла ошибка при обновлении: {e}")
        import traceback
        traceback.print_exc()
        print("\nПожалуйста, проверьте совместимость всех модулей.")

if __name__ == "__main__":
    # Проверяем наличие необходимых пакетов
    requests = import_or_install("requests")
    if not requests:
        print("⚠️ Предупреждение: Не удалось установить пакет requests. Некоторые функции могут быть недоступны.")
    
    main()