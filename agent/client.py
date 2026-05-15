from dotenv import load_dotenv
load_dotenv()

import asyncio
from agents.mcp import MCPServerStdio

async def main():
    async with MCPServerStdio(
        params={
            "command": "uv",
            "args": ["run", "mcp_server/server.py"]
        },
    ) as mcp_server:
        try:
            print("Step 1: Fetching shift data...")
            result = await mcp_server.call_tool("fetch_shift_data", {"shift_id": 1})
            shift_data = result.content[0].text

            print("Step 2: Analyzing shift health...")
            result = await mcp_server.call_tool("analyze_shift_health", {"shift_data_json": shift_data})
            analysis = result.content[0].text

            print("Step 3: Generating report...")
            result = await mcp_server.call_tool("generate_shift_report", {
                "shift_data_json": shift_data,
                "analysis_json": analysis
            })
            report = result.content[0].text

            print("\n" + "=" * 60)
            print(report)

        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

asyncio.run(main())
