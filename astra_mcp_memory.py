# -*- coding: utf-8 -*-
"""Local MCP memory system using FAISS and sentence-transformers.

This module provides semantic memory capabilities for Astra by storing
embeddings in a FAISS index and keeping metadata in a JSON file.
The design follows the MCP (Model Context Protocol) approach but works
locally without a network service.
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional

try:
    import faiss  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    faiss = None

try:
    from sentence_transformers import SentenceTransformer  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    SentenceTransformer = None

try:
    import numpy as np
except Exception:  # pragma: no cover - optional dependency
    np = None

# Configuration for the MCP memory
MCP_CONFIG = {
    "embedding_model": "all-MiniLM-L6-v2",
    "vector_dim": 384,
    "similarity_threshold": 0.6,
    "dedup_threshold": 0.95,
    "max_memories": 50000,
    "backup_frequency": "daily",
}

VECTOR_DIR = os.path.join("astra_vector_store")
INDEX_FILE = os.path.join(VECTOR_DIR, "faiss_index.bin")
META_FILE = os.path.join(VECTOR_DIR, "metadata.json")


class AstraMCPMemory:
    """Semantic memory manager backed by FAISS."""

    def __init__(self, data_dir: str = "astra_data") -> None:
        self.data_dir = data_dir
        self.vector_dim = MCP_CONFIG["vector_dim"]
        self.embeddings: Optional[SentenceTransformer] = None
        self.index = None
        self.metadata: Dict[str, Dict] = {}
        self._load_dependencies()
        self._ensure_dirs()
        self._load_index()
        self._load_metadata()

    # ------------------------------------------------------------------
    def _load_dependencies(self) -> None:
        """Lazily loads heavy dependencies if available."""
        global faiss, SentenceTransformer
        if faiss is None or SentenceTransformer is None:
            print("AstraMCPMemory: FAISS or sentence-transformers not available")
        else:
            self.embeddings = SentenceTransformer(MCP_CONFIG["embedding_model"])

    def _ensure_dirs(self) -> None:
        if not os.path.exists(VECTOR_DIR):
            os.makedirs(VECTOR_DIR)

    def _load_index(self) -> None:
        if faiss is None:
            return
        if os.path.exists(INDEX_FILE):
            self.index = faiss.read_index(INDEX_FILE)
        else:
            self.index = faiss.IndexFlatIP(self.vector_dim)

    def _load_metadata(self) -> None:
        if os.path.exists(META_FILE):
            with open(META_FILE, "r", encoding="utf-8") as f:
                try:
                    self.metadata = json.load(f)
                except json.JSONDecodeError:
                    self.metadata = {}
        else:
            self.metadata = {}

    def _save_index(self) -> None:
        if faiss is None or self.index is None:
            return
        faiss.write_index(self.index, INDEX_FILE)

    def _save_metadata(self) -> None:
        with open(META_FILE, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)

    # ------------------------------------------------------------------
    def _embed(self, text: str) -> Optional[np.ndarray]:
        if self.embeddings is None or np is None:
            return None
        vector = self.embeddings.encode([text], normalize_embeddings=True)
        return vector.astype("float32")

    def store_memory(
        self,
        text: str,
        source: str,
        emotion: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> str:
        """Stores a memory fragment and returns its ID."""
        if faiss is None or self.embeddings is None or self.index is None:
            # Fallback: just store metadata without vector search
            memory_id = str(uuid.uuid4())
            self.metadata[memory_id] = {
                "text": text,
                "source": source,
                "emotion": emotion,
                "tags": tags or [],
                "created_at": datetime.utcnow().isoformat(),
            }
            self._save_metadata()
            return memory_id

        vector = self._embed(text)
        if vector is None:
            return ""
        memory_id = str(uuid.uuid4())
        self.index.add(vector)
        self.metadata[memory_id] = {
            "text": text,
            "source": source,
            "emotion": emotion,
            "tags": tags or [],
            "created_at": datetime.utcnow().isoformat(),
        }
        self._save_index()
        self._save_metadata()
        return memory_id

    def semantic_search(
        self, query: str, top_k: int = 3, min_score: float = 0.6
    ) -> List[Dict]:
        if faiss is None or self.embeddings is None or self.index is None:
            return []
        if self.index.ntotal == 0:
            return []
        query_vec = self._embed(query)
        if query_vec is None:
            return []
        scores, indices = self.index.search(query_vec, top_k)
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1 or score < min_score:
                continue
            # metadata keys are not guaranteed to match index order when loaded.
            mem_id = list(self.metadata.keys())[idx]
            meta = self.metadata.get(mem_id, {})
            results.append({"id": mem_id, "score": float(score), **meta})
        return results

    def migrate_from_files(self) -> bool:
        """Migrates existing *.txt memories into the vector store."""
        data_path = os.path.join(self.data_dir)
        files = [f for f in os.listdir(data_path) if f.endswith(".txt")]
        success = True
        for fname in files:
            path = os.path.join(data_path, fname)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    text = f.read()
                self.store_memory(text, fname)
            except Exception:
                success = False
        return success

    def get_stats(self) -> Dict:
        return {
            "memories": len(self.metadata),
            "index_size": getattr(self.index, "ntotal", 0) if self.index else 0,
        }
