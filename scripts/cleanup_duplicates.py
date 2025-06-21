#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import astra_memory


def cleanup_emotion_memory():
    mem = astra_memory.AstraMemory()
    norm_dict = {}
    for entry in mem.emotion_memory:
        norm = mem._normalize_phrase(entry.get("trigger", ""))
        if norm in norm_dict:
            existing = norm_dict[norm]
            if entry.get("emotion"):
                emotions = entry["emotion"] if isinstance(entry["emotion"], list) else [entry["emotion"]]
                existing_emotions = existing.get("emotion", [])
                if not isinstance(existing_emotions, list):
                    existing_emotions = [existing_emotions]
                existing["emotion"] = list(dict.fromkeys(existing_emotions + emotions))
            if entry.get("tone") and not existing.get("tone"):
                existing["tone"] = entry["tone"]
            if entry.get("subtone"):
                subs = entry["subtone"] if isinstance(entry["subtone"], list) else [entry["subtone"]]
                existing_subs = existing.get("subtone", [])
                if not isinstance(existing_subs, list):
                    existing_subs = [existing_subs]
                existing["subtone"] = list(dict.fromkeys(existing_subs + subs))
            if entry.get("flavor"):
                fl = entry["flavor"] if isinstance(entry["flavor"], list) else [entry["flavor"]]
                existing_fl = existing.get("flavor", [])
                if not isinstance(existing_fl, list):
                    existing_fl = [existing_fl]
                existing["flavor"] = list(dict.fromkeys(existing_fl + fl))
        else:
            new_entry = entry.copy()
            new_entry["trigger"] = norm
            norm_dict[norm] = new_entry
    mem.emotion_memory = list(norm_dict.values())
    mem.save_json_file(astra_memory.EMOTION_MEMORY_FILE, mem.emotion_memory)
    print("Duplicates cleaned. Total entries:", len(mem.emotion_memory))


if __name__ == "__main__":
    cleanup_emotion_memory()
