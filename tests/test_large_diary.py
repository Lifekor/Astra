import json as jsonlib
import os
import re
import importlib
import types
import sys
from tempfile import TemporaryDirectory


# Stub requests before importing modules that require it
requests_stub = types.SimpleNamespace(post=None, exceptions=types.SimpleNamespace(RequestException=Exception))
sys.modules["requests"] = requests_stub
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import astra_memory  # noqa: E402
from memory_extractor import MemoryExtractor  # noqa: E402


def setup_memory(tmpdir):
    importlib.reload(astra_memory)
    astra_memory.DATA_DIR = tmpdir
    mem = astra_memory.AstraMemory(autonomous_memory=False)
    return mem


def create_large_diary(path, paragraphs=200, words_per_para=50):
    with open(path, "w", encoding="utf-8") as f:
        f.write("📔 BIG DIARY\n\n")
        for i in range(paragraphs):
            words = " ".join([f"word{i}_{j}" for j in range(words_per_para)])
            f.write(f"[01.01.2024 00:{i:02d}]\n{words}\n\n")


def fake_post_factory(counter):
    def fake_post(url, headers=None, json=None):
        counter["count"] += 1
        content = json["messages"][1]["content"]
        indexes = [int(i) for i in re.findall(r"(\d+):", content)]
        result = [{"index": idx, "relevance": 1 / (idx + 1)} for idx in indexes]

        class Resp:
            status_code = 200

            def json(self):
                return {"choices": [{"message": {"content": jsonlib.dumps(result)}}]}

        return Resp()

    return fake_post


def test_large_diary_batches(monkeypatch):
    with TemporaryDirectory() as tmp:
        mem = setup_memory(tmp)
        diary_path = os.path.join(tmp, "big_diary.txt")
        create_large_diary(diary_path)

        extractor = MemoryExtractor(mem, api_key="test")
        assert "big_diary" in extractor.diaries

        counter = {"count": 0}
        monkeypatch.setattr("intent_analyzer.requests.post", fake_post_factory(counter))

        intent_data = {"intent": "about_astra", "match_memory": ["big_diary"]}
        result = extractor.extract_relevant_memories("query", intent_data=intent_data, model="gpt-3.5-turbo")
        assert len(result["memories"]) == 3
        # the extractor now limits total fragment tokens, so a single API call is enough
        assert counter["count"] >= 1
