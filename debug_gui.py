import json
import os
import re
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from astra_memory import AstraMemory
from emotional_analyzer import EmotionalAnalyzer
from reply_composer import compose_layered_reply


class DebugGUI:
    def __init__(self):
        self.memory = AstraMemory()
        self.analyzer = EmotionalAnalyzer(self.memory)
        self.root = tk.Tk()
        self.root.title("Astra Style Debugger")

        self._build_widgets()

    def _build_widgets(self):
        # Labels for columns
        input_frame = ttk.Frame(self.root)
        output_frame = ttk.Frame(self.root)
        log_frame = ttk.Frame(self.root)

        input_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        output_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        log_frame.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")

        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=1)
        self.root.rowconfigure(0, weight=1)

        ttk.Label(input_frame, text="Ввод").pack()
        ttk.Label(output_frame, text="Эмоциональный вывод").pack()
        ttk.Label(log_frame, text="Отладка").pack()

        self.input_text = ScrolledText(input_frame, height=10)
        self.input_text.pack(fill="both", expand=True)

        self.output_text = ScrolledText(output_frame, height=10)
        self.output_text.pack(fill="both", expand=True)

        self.log_text = ScrolledText(log_frame, height=10)
        self.log_text.pack(fill="both", expand=True)

        btn = ttk.Button(self.root, text="Сгенерировать", command=self.process)
        btn.grid(row=1, column=0, columnspan=3, pady=5)

        # Configure tags for coloring
        self.output_text.tag_configure("tone", foreground="blue")
        self.output_text.tag_configure("subtone", foreground="purple")
        self.output_text.tag_configure("flavor", foreground="goldenrod")
        self.output_text.tag_configure("micro", font=("TkDefaultFont", 10, "italic"))

    def highlight_microexpressions(self, text):
        for match in re.finditer(r"\([^\)]+\)", text):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.output_text.tag_add("micro", start, end)

    def process(self):
        phrase = self.input_text.get("1.0", tk.END).strip()
        if not phrase:
            return

        state = self.analyzer.analyze_message(phrase)
        reply = compose_layered_reply(state, self.memory, phrase)

        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, reply)
        self.highlight_microexpressions(reply)

        explanation = (
            f"Tone: {state.get('tone')}\n"
            f"Subtone: {', '.join(state.get('subtone', []))}\n"
            f"Flavor: {', '.join(state.get('flavor', []))}\n"
        )
        self.output_text.insert(tk.END, "\n\n" + explanation, ("tone",))

        triggers = [t["trigger"] for t in self.memory.trigger_phrases if t.get("trigger", "").lower() in phrase.lower()]
        memory_used = []
        if state.get("tone"):
            memory_used.append("tone_memory.json")
        if state.get("subtone"):
            memory_used.append("subtone_memory.json")
        if state.get("flavor"):
            memory_used.append("flavor_memory.json")

        log_entry = {
            "phrase": phrase,
            "state": state,
            "reply": reply,
            "triggers": triggers,
            "memory_used": memory_used,
        }
        self.log_text.insert(tk.END, json.dumps(log_entry, ensure_ascii=False, indent=2) + "\n")

        self.save_debug_log(log_entry)

    def save_debug_log(self, entry):
        path = "debug_output.json"
        data = []
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = []
        data.append(entry)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    gui = DebugGUI()
    gui.run()

