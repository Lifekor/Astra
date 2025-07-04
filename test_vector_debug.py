#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Отладочный тест для векторной памяти
"""

print("🔍 Тест векторной памяти...")

try:
    from astra_mcp_memory import AstraMCPMemory

    # Инициализация
    mcp = AstraMCPMemory()
    print(f"📊 Статистика: {mcp.get_stats()}")

    # Проверка компонентов
    print(f"🧠 Embeddings: {mcp.embeddings is not None}")
    print(f"📚 Index: {mcp.index is not None}")

    # Тест поиска
    if mcp.embeddings and mcp.index:
        print("\n🔍 Выполняем поиск...")
        results = mcp.semantic_search("создание домика", top_k=5, min_score=0.1)
        print(f"🎯 Найдено: {len(results)} результатов")

        for i, result in enumerate(results, 1):
            print(f"\n{i}. Score: {result.get('score', 0):.3f}")
            print(f"   Source: {result.get('source', 'unknown')}")
            text = result.get("text", "")
            print(f"   Text: {text[:150]}...")
    else:
        print("❌ Компоненты не работают")

except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
except Exception as e:
    print(f"❌ Другая ошибка: {e}")

print("\n🔍 Проверка зависимостей...")
try:
    import faiss

    print("✅ FAISS доступен")
except ImportError:
    print("❌ FAISS не установлен")

try:
    from sentence_transformers import SentenceTransformer

    print("✅ SentenceTransformers доступен")
except ImportError:
    print("❌ SentenceTransformers не установлен")

try:
    import numpy as np

    print("✅ NumPy доступен")
except ImportError:
    print("❌ NumPy не установлен")
