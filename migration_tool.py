"""Utility script to migrate existing text memories to the MCP vector store."""
import argparse
from astra_mcp_memory import AstraMCPMemory


def main(data_dir: str) -> None:
    mcp = AstraMCPMemory(data_dir)
    success = mcp.migrate_from_files()
    stats = mcp.get_stats()
    print("Migration success" if success else "Migration failed")
    print(f"Stored memories: {stats['memories']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate Astra memories to MCP")
    parser.add_argument("--data-dir", default="astra_data", help="Path to diary directory")
    args = parser.parse_args()
    main(args.data_dir)
