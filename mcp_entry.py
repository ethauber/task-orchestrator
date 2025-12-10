import sys
import os

# Get the absolute path to the project root (where this script resides)
project_root = os.path.dirname(os.path.abspath(__file__))

# Explicitly add the project root to sys.path
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import the MCP server instance
try:
    from backend.mcp_server import mcp
except ImportError as e:
    print(f"Error importing backend: {e}", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
