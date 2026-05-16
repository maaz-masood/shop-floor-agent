from dotenv import load_dotenv
load_dotenv()

from mcp.server.fastmcp import FastMCP
import sqlite3
import json
import os
import httpx

mcp = FastMCP("Shop Floor Intelligence")
DB_PATH = "database/shop_floor.db"

@mcp.tool()
def fetch_shift_data(shift_id: int) -> str:
    """
    Fetch aggregated machine production and issue data
    for a specific shift. Call this FIRST before any
    analysis or report generation.
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

    # Aggregated production per machine
    cursor.execute("""
        SELECT 
            M.machine_id,
            M.machine_name,
            M.purpose,
            M.last_maintenance,
            M.manufacturing_date,
            O.operator_name,
            O.experience_years,
            SUM(P.units_produced) as total_units,
            SUM(P.defective_units) as total_defects,
            I.issue_type,
            I.duration_minutes,
            I.is_recurring,
            I.resolved
        FROM machines M
        JOIN production P ON M.machine_id = P.machine_id
        LEFT JOIN issues I ON M.machine_id = I.machine_id
            AND I.shift_id = ?
        JOIN operators O ON M.operator_id = O.operator_id
        WHERE P.shift_id = ?
        GROUP BY M.machine_id
    """, (shift_id, shift_id))

    machines = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return json.dumps({
        "shift": shift,
        "machines": machines
    }, indent=2)


@mcp.tool()
def analyze_shift_health(shift_data_json: str) -> str:
    """
    Analyze shift data and identify machines with high
    defect rates, low production, or unresolved issues.
    Call this AFTER fetch_shift_data.
    """
    data = json.loads(shift_data_json)
    machines = data["machines"]

    alerts = []
    highlights = []
    TARGET_UNITS = 500   # adjusted for multi-reading shifts
    MAX_DEFECT_RATE = 0.05

    for m in machines:
        name = m["machine_name"]
        produced = m["total_units"] or 0
        defective = m["total_defects"] or 0
        defect_rate = defective / produced if produced > 0 else 0

        if defect_rate > MAX_DEFECT_RATE:
            alerts.append({
                "machine": name,
                "alert": "HIGH DEFECT RATE",
                "defect_rate": f"{defect_rate:.1%}",
                "action": "Inspect immediately"
            })

        if produced < TARGET_UNITS:
            alerts.append({
                "machine": name,
                "alert": "BELOW PRODUCTION TARGET",
                "produced": produced,
                "target": TARGET_UNITS,
                "action": "Review workflow"
            })

        if m["issue_type"] and m["is_recurring"] and not m["resolved"]:
            alerts.append({
                "machine": name,
                "alert": "UNRESOLVED RECURRING ISSUE",
                "issue": m["issue_type"],
                "action": "Schedule maintenance"
            })

        if defect_rate <= MAX_DEFECT_RATE and produced >= TARGET_UNITS:
            highlights.append({
                "machine": name,
                "status": "Performing well",
                "units": produced
            })

    return json.dumps({
        "total_alerts": len(alerts),
        "alerts": alerts,
        "highlights": highlights
    }, indent=2)


@mcp.tool()
async def generate_shift_report(
    shift_data_json: str,
    analysis_json: str
) -> str:
    """
    Generate a professional shift handover report.
    Call this LAST after fetch_shift_data and
    analyze_shift_health.
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
                        "content": "You are a manufacturing operations expert. Generate clear professional shift handover reports."
                    },
                    {
                        "role": "user",
                        "content": f"""Generate a shift handover report.

SHIFT DATA:
{shift_data_json}

ANALYSIS:
{analysis_json}

Format with these sections:
# Shift Handover Report
## Shift Summary
## Production Overview
## Alerts and Issues
## Well Performing Machines
## Recommended Actions for Next Shift"""
                    }
                ]
            },
            timeout=30.0
        )
        return response.json()["choices"][0]["message"]["content"]


if __name__ == "__main__":
    mcp.run(transport="stdio")