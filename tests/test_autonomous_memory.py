import json
import importlib
from tempfile import TemporaryDirectory

import pytest

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import astra_memory
import types
sys.modules.setdefault("requests", types.ModuleType("requests"))
dotenv_stub = types.ModuleType("dotenv")
dotenv_stub.load_dotenv = lambda *args, **kwargs: None
sys.modules.setdefault("dotenv", dotenv_stub)
import astra_chat


def setup_memory(tmpdir, autonomous=True):
    importlib.reload(astra_memory)
    astra_memory.DATA_DIR = tmpdir
    mem = astra_memory.AstraMemory(autonomous_memory=autonomous)
    return mem


def load_emotions(mem):
    path = mem.get_file_path(astra_memory.EMOTION_MEMORY_FILE)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def test_auto_add_emotion():
    with TemporaryDirectory() as tmp:
        mem = setup_memory(tmp)
        phrase = "ты моя радость"
        mem.auto_update_emotion(phrase, "радость")
        data = load_emotions(mem)
        assert any(i.get("trigger") == phrase for i in data)


def test_auto_overwrite_emotion():
    with TemporaryDirectory() as tmp:
        mem = setup_memory(tmp)
        phrase = "я скучаю"
        mem.auto_update_emotion(phrase, "тоска")
        mem.auto_update_emotion(phrase, "радость")
        data = load_emotions(mem)
        entry = [i for i in data if i.get("trigger") == phrase][0]
        assert entry.get("emotion") == ["радость"]


def test_autonomous_disabled():
    with TemporaryDirectory() as tmp:
        mem = setup_memory(tmp, autonomous=False)
        phrase = "ты прекрасна"
        mem.auto_update_emotion(phrase, "восхищение")
        data = load_emotions(mem)
        assert all(i.get("trigger") != phrase for i in data)


def test_no_update_when_state_same():
    with TemporaryDirectory() as tmp:
        mem = setup_memory(tmp)
        chat = astra_chat.AstraChat(mem)
        before = load_emotions(mem)
        chat.process_user_message("Привет, как дела?")
        after = load_emotions(mem)
        assert after == before
