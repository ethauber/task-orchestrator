import sys
import os
import asyncio

sys.path.append(os.getcwd())


async def main():
    try:
        from backend.mcp_server import mcp

        print("MCP Server imported successfully.")
        tools = await mcp.list_tools()
        print(f"Found {len(tools)} tools:")
        for t in tools:
            print(f"- {t.name}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
