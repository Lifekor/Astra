# MCP Memory System for Astra

This module introduces a local semantic memory based on FAISS and
`sentence-transformers`.  Memories are stored as embeddings in
`astra_vector_store/faiss_index.bin` with metadata in
`astra_vector_store/metadata.json`.

## Quick start

1. Install the dependencies:

```bash
pip install -r requirements_mcp.txt
```

2. Migrate existing memories:

```bash
python migration_tool.py --data-dir astra_data
```

3. Run `astra_app.py` as usual.  The `MemoryExtractor` will use the
semantic store if available.
