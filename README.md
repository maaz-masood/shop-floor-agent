# Shop Floor Intelligence Agent

An autonomous AI agent that monitors manufacturing shop floor data and automatically generates shift handover reports.

## Problem
Supervisors spend 30-45 minutes manually compiling shift reports. Information gets missed. Next shift starts without full context.

## Solution
AI agent that monitors machine data, detects anomalies, and generates complete handover reports automatically.

## Architecture
\`\`\`
realtime_simulator.py  →  inserts machine readings every 30 seconds
database/shop_floor.db →  SQLite with 5 tables
mcp_server/server.py   →  3 MCP tools (fetch, analyze, report)
agent/client.py        →  orchestrates tools via OpenAI Agents SDK
reports/               →  generated shift reports saved here
\`\`\`

## Tech Stack
- Python
- MCP (Model Context Protocol) + FastMCP
- OpenAI Agents SDK
- SQLite
- OpenRouter API
- uv