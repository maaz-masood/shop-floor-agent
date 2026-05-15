from dotenv import load_dotenv
load_dotenv()

from mcp.server.fastmcp import FastMCP
import sqlite3
import json
import os
import httpx

mcp = FastMCP("Shop Floor Intelligence")

DB_PATH = "database/shop_floor.db"

# ── Tool 1 — Fetch shift data ──
@mcp.tool()
def fetch_shift_data(shift_id: int) -> str:
    """
    Fetch all machine production and issue data
    for a specific shift from the database.
    Returns a JSON string with complete shift details.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Shift info
    cursor.execute("""
        SELECT S.*, O.operator_name 
        FROM shifts S
        JOIN operators O ON S.operator_id = O.operator_id
        WHERE S.shift_id = ?
    """, (shift_id,))
    shift = dict(cursor.fetchone())

    # Machine + production + issues + operator
    cursor.execute("""
        SELECT 
            M.machine_id, M.machine_name, M.purpose,
            M.last_maintenance, M.manufacturing_date,
            P.units_produced, P.defective_units, P.shift_date,
            I.issue_type, I.duration_minutes, 
            I.is_recurring, I.resolved,
            O.operator_name, O.experience_years
        FROM machines M
        JOIN production P ON M.machine_id = P.machine_id
        LEFT JOIN issues I ON M.machine_id = I.machine_id 
            AND I.shift_id = ?
        JOIN operators O ON M.operator_id = O.operator_id
        WHERE P.shift_id = ?
    """, (shift_id, shift_id))

    machines = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return json.dumps({
        "shift": shift,
        "machines": machines
    }, indent=2)


# ── Tool 2 — Analyze shift health ──
@mcp.tool()
def analyze_shift_health(shift_data_json: str) -> str:
    """
    Analyze shift data and identify machines with:
    - High defect rates (above 5%)
    - Unresolved recurring issues
    - Production below target (100 units)
    Returns a JSON summary of alerts and highlights.
    """
    data = json.loads(shift_data_json)
    machines = data["machines"]

    alerts = []
    highlights = []
    TARGET_UNITS = 100
    MAX_DEFECT_RATE = 0.05  # 5%

    for m in machines:
        name = m["machine_name"]
        produced = m["units_produced"]
        defective = m["defective_units"]
        defect_rate = defective / produced if produced > 0 else 0

        # Check defect rate
        if defect_rate > MAX_DEFECT_RATE:
            alerts.append({
                "machine": name,
                "alert": "HIGH DEFECT RATE",
                "defect_rate": f"{defect_rate:.1%}",
                "action": "Inspect immediately"
            })

        # Check production target
        if produced < TARGET_UNITS:
            alerts.append({
                "machine": name,
                "alert": "BELOW PRODUCTION TARGET",
                "produced": produced,
                "target": TARGET_UNITS,
                "action": "Review workflow"
            })

        # Check unresolved recurring issues
        if m["issue_type"] and m["is_recurring"] and not m["resolved"]:
            alerts.append({
                "machine": name,
                "alert": "UNRESOLVED RECURRING ISSUE",
                "issue": m["issue_type"],
                "duration": f"{m['duration_minutes']} minutes",
                "action": "Schedule maintenance"
            })

        # Highlight well performing machines
        if defect_rate <= MAX_DEFECT_RATE and produced >= TARGET_UNITS:
            highlights.append({
                "machine": name,
                "status": "✅ Performing well",
                "units": produced
            })

    return json.dumps({
        "total_alerts": len(alerts),
        "alerts": alerts,
        "highlights": highlights
    }, indent=2)


# ── Tool 3 — Generate shift report ──
@mcp.tool()
async def generate_shift_report(
    shift_data_json: str,
    analysis_json: str
) -> str:
    """
    Generate a professional shift handover report
    using AI to synthesize shift data and analysis.
    Returns a formatted markdown report for the next shift supervisor.
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openrouter/auto",
                "messages": [
                    {
                        "role": "system",
                        "content": """You are a manufacturing operations expert.
                        Generate clear, professional shift handover reports.
                        Be specific, factual, and actionable."""
                    },
                    {
                        "role": "user",
                        "content": f"""Generate a shift handover report for the next supervisor.

SHIFT DATA:
{shift_data_json}

ANALYSIS:
{analysis_json}

Format the report with these sections:
# Shift Handover Report
## Shift Summary
## Production Overview (table format)
## Alerts & Issues Requiring Attention
## Well Performing Machines
## Recommended Actions for Next Shift
## Notes for Next Supervisor"""
                    }
                ]
            },
            timeout=30.0
        )
        data = response.json()
        if "choices" not in data:
            raise ValueError(f"OpenRouter error: {data}")
        return data["choices"][0]["message"]["content"]


if __name__ == "__main__":
    mcp.run(transport="stdio")