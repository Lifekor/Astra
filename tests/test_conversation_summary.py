import json
import importlib
from tempfile import TemporaryDirectory
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import astra_memory
import conversation_manager


def setup_memory(tmpdir):
    importlib.reload(astra_memory)
    astra_memory.DATA_DIR = tmpdir
    mem = astra_memory.AstraMemory(autonomous_memory=False)
    return mem


def test_history_summarization_and_context():
    with TemporaryDirectory() as tmp:
        mem = setup_memory(tmp)
        cm = conversation_manager.ConversationManager(mem)
        for i in range(7):
            cm.add_message("user", f"msg{i}")
        # Принудительно создаем сводку, чтобы уменьшить размер истории
        cm.summarize_history(max_recent=5, summary_words=5)
        path = mem.get_file_path("conversation_summaries.jsonl")
        assert os.path.exists(path)
        with open(path, "r", encoding="utf-8") as f:
            lines = [json.loads(line) for line in f if line.strip()]
        assert len(lines) == 1
        assert "summary" in lines[0]
        # После сводки сохраняются только последние 5 сообщений
        assert len(cm.full_conversation_history) <= 5

        cm.add_message("user", "new message")
        ctx = cm.get_relevant_context("hello")
        assert any("Сводка предыдущего диалога" in m["content"] for m in ctx)
