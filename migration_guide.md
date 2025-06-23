# Migration Guide

This document describes how to migrate existing diary files from
`astra_data/` to the new MCP vector store.

1. **Backup your data.**
   Copy the entire `astra_data/` directory to a safe location.
2. **Install MCP dependencies.**
   ```bash
   pip install -r requirements_mcp.txt
   ```
3. **Run the migration tool.**
   ```bash
   python migration_tool.py --data-dir astra_data
   ```
   This will populate `astra_vector_store/` with a FAISS index and
   metadata file.
4. **Verify results.**
   Check the output of the migration tool to see how many memories were
   stored.
5. **Launch Astra.**
   Start `astra_app.py` normally. The application will prefer the vector
   store if it exists.
