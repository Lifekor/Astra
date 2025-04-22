import json
import os
import sys

# Импортируем классы из astra_app.py
try:
    from astra_app import AstraMemory, FLAVOR_MEMORY_FILE, TONE_MEMORY_FILE, SUBTONE_MEMORY_FILE, EMOTION_MEMORY_FILE
except ImportError:
    print("Ошибка: Не удалось импортировать классы из astra_app.py. Убедитесь, что файл находится в той же директории.")
    sys.exit(1)

class AstraTester:
    """Класс для тестирования функциональности Astra"""
    
    def __init__(self):
        """Инициализация тестера"""
        self.memory = AstraMemory()
        print("AstraTester инициализирован.")
    
    def check_flavor_structure(self):
        """Проверяет структуру flavor в памяти"""
        print("\n=== Проверка структуры flavor ===")
        if not self.memory.flavor_memory:
            print("Предупреждение: flavor_memory пуст!")
            return False
        
        print(f"Найдено {len(self.memory.flavor_memory)} flavor.")
        
        # Проверяем структуру первого flavor
        first_flavor = self.memory.flavor_memory[0]
        print("Структура первого flavor:")
        for key, value in first_flavor.items():
            if key == 'examples':
                print(f"  {key}: {len(value)} примеров")
            else:
                print(f"  {key}: {value}")
        
        # Проверяем метод get_flavor_by_label
        label = first_flavor.get('label')
        result = self.memory.get_flavor_by_label(label)
        print(f"\nПроверка get_flavor_by_label('{label}'):")
        if result:
            print(f"  Найден flavor с label '{label}'")
            return True
        else:
            print(f"  Ошибка: Не найден flavor с label '{label}'")
            return False
    
    def check_subtone_structure(self):
        """Проверяет структуру subtone в памяти"""
        print("\n=== Проверка структуры subtone ===")
        if not self.memory.subtone_memory:
            print("Предупреждение: subtone_memory пуст!")
            return False
        
        print(f"Найдено {len(self.memory.subtone_memory)} subtone.")
        
        # Проверяем структуру первого subtone
        first_subtone = self.memory.subtone_memory[0]
        print("Структура первого subtone:")
        for key, value in first_subtone.items():
            if key == 'examples':
                print(f"  {key}: {len(value)} примеров")
            else:
                print(f"  {key}: {value}")
        
        # Проверяем метод get_subtone_by_label
        label = first_subtone.get('label')
        result = self.memory.get_subtone_by_label(label)
        print(f"\nПроверка get_subtone_by_label('{label}'):")
        if result:
            print(f"  Найден subtone с label '{label}'")
            return True
        else:
            print(f"  Ошибка: Не найден subtone с label '{label}'")
            return False
    
    def check_emotion_memory_references(self):
        """Проверяет, как в emotion_memory ссылаются на flavor, tone и subtone"""
        print("\n=== Проверка ссылок в emotion_memory ===")
        if not self.memory.emotion_memory:
            print("Предупреждение: emotion_memory пуст!")
            return False
        
        print(f"Найдено {len(self.memory.emotion_memory)} записей в emotion_memory.")
        
        # Ищем записи с flavor, tone и subtone
        flavor_entries = [entry for entry in self.memory.emotion_memory if 'flavor' in entry]
        tone_entries = [entry for entry in self.memory.emotion_memory if 'tone' in entry]
        subtone_entries = [entry for entry in self.memory.emotion_memory if 'subtone' in entry]
        
        print(f"Записей с flavor: {len(flavor_entries)}")
        print(f"Записей с tone: {len(tone_entries)}")
        print(f"Записей с subtone: {len(subtone_entries)}")
        
        # Проверяем структуру flavor в emotion_memory
        if flavor_entries:
            print("\nПример записи с flavor:")
            entry = flavor_entries[0]
            print(f"  trigger: '{entry.get('trigger')}'")
            print(f"  flavor: {entry.get('flavor')}")
            
            # Проверяем, является ли flavor строкой или списком строк
            flavor = entry.get('flavor')
            if isinstance(flavor, list):
                print("  flavor записан как список, проверяем первый элемент")
                if flavor:
                    first_flavor = flavor[0]
                    print(f"  Первый flavor: '{first_flavor}'")
                    
                    # Проверяем, существует ли такой flavor в flavor_memory
                    flavor_obj = self.memory.get_flavor_by_label(first_flavor)
                    if flavor_obj:
                        print(f"  Flavor '{first_flavor}' найден в flavor_memory")
                    else:
                        print(f"  Ошибка: Flavor '{first_flavor}' не найден в flavor_memory")
            elif isinstance(flavor, str):
                print(f"  flavor записан как строка: '{flavor}'")
                
                # Проверяем, существует ли такой flavor в flavor_memory
                flavor_obj = self.memory.get_flavor_by_label(flavor)
                if flavor_obj:
                    print(f"  Flavor '{flavor}' найден в flavor_memory")
                else:
                    print(f"  Ошибка: Flavor '{flavor}' не найден в flavor_memory")
            else:
                print(f"  Ошибка: Неожиданный тип flavor: {type(flavor)}")
        
        # Аналогичная проверка для subtone
        if subtone_entries:
            print("\nПример записи с subtone:")
            entry = subtone_entries[0]
            print(f"  trigger: '{entry.get('trigger')}'")
            print(f"  subtone: {entry.get('subtone')}")
        
        return True
    
    def test_add_emotion(self):
        """Тестирует добавление эмоции к фразе"""
        print("\n=== Тестирование add_emotion_to_phrase ===")
        
        test_phrase = "Тестовая фраза для проверки добавления эмоции"
        test_emotion = "тестовая_эмоция"
        
        # Добавляем эмоцию к фразе
        result = self.memory.add_emotion_to_phrase(test_phrase, test_emotion)
        print(f"Добавление эмоции '{test_emotion}' к фразе: {result}")
        
        # Проверяем, добавилась ли фраза
        added = False
        for entry in self.memory.emotion_memory:
            if entry.get('trigger') == test_phrase:
                added = True
                print(f"Найдена запись: {entry}")
                break
        
        if added:
            print("Тест пройден: Фраза добавлена в emotion_memory")
        else:
            print("Тест не пройден: Фраза не добавлена в emotion_memory")
        
        return added
    
    def test_add_flavor(self):
        """Тестирует добавление flavor к фразе"""
        print("\n=== Тестирование добавления flavor ===")
        
        if not self.memory.flavor_memory:
            print("Предупреждение: flavor_memory пуст, невозможно выполнить тест!")
            return False
        
        test_phrase = "Тестовая фраза для проверки добавления flavor"
        test_flavor = self.memory.flavor_memory[0].get('label')
        
        # Добавляем flavor к фразе
        result = self.memory.add_emotion_to_phrase(test_phrase, None, flavor=test_flavor)
        print(f"Добавление flavor '{test_flavor}' к фразе: {result}")
        
        # Проверяем, добавилась ли фраза
        added = False
        for entry in self.memory.emotion_memory:
            if entry.get('trigger') == test_phrase:
                added = True
                print(f"Найдена запись: {entry}")
                if 'flavor' in entry:
                    flavor = entry.get('flavor')
                    if isinstance(flavor, list) and test_flavor in flavor:
                        print(f"Flavor '{test_flavor}' добавлен в список")
                    elif isinstance(flavor, str) and flavor == test_flavor:
                        print(f"Flavor '{test_flavor}' добавлен как строка")
                    else:
                        print(f"Ошибка: Flavor не найден в записи")
                        added = False
                else:
                    print("Ошибка: В записи нет поля 'flavor'")
                    added = False
                break
        
        if added:
            print("Тест пройден: Flavor добавлен к фразе")
        else:
            print("Тест не пройден: Flavor не добавлен к фразе")
        
        return added
    
    def test_decide_response_emotion(self):
        """Тестирует определение эмоций для ответа"""
        print("\n=== Тестирование decide_response_emotion ===")
        
        # Берем первую фразу из emotion_memory
        if not self.memory.emotion_memory:
            print("Предупреждение: emotion_memory пуст, невозможно выполнить тест!")
            return False
        
        test_entry = self.memory.emotion_memory[0]
        test_phrase = test_entry.get('trigger')
        
        print(f"Тестируем фразу: '{test_phrase}'")
        
        # Вызываем метод decide_response_emotion
        result = self.memory.decide_response_emotion(test_phrase)
        print("Результат decide_response_emotion:")
        for key, value in result.items():
            print(f"  {key}: {value}")
        
        # Проверяем, есть ли в результате какие-то данные
        if result and (result.get('tone') or result.get('emotion') or 
                       result.get('subtone') or result.get('flavor')):
            print("Тест пройден: Метод вернул эмоциональный контекст")
            return True
        else:
            print("Тест не пройден: Метод не вернул эмоциональный контекст")
            return False
    
    def run_all_tests(self):
        """Запускает все тесты"""
        print("=== Запуск всех тестов ===\n")
        
        tests = [
            self.check_flavor_structure,
            self.check_subtone_structure,
            self.check_emotion_memory_references,
            self.test_add_emotion,
            self.test_add_flavor,
            self.test_decide_response_emotion
        ]
        
        results = []
        for test in tests:
            result = test()
            results.append(result)
        
        print("\n=== Результаты тестов ===")
        total_tests = len(tests)
        passed_tests = sum(1 for r in results if r)
        print(f"Пройдено {passed_tests} из {total_tests} тестов")
        
        if passed_tests == total_tests:
            print("Все тесты пройдены успешно! Скрипт работает правильно.")
        else:
            print(f"Внимание: {total_tests - passed_tests} тестов не пройдены.")


if __name__ == "__main__":
    tester = AstraTester()
    tester.run_all_tests()