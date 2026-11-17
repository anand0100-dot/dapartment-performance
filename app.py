import os
import time

import psycopg
from flask import Flask, jsonify, render_template_string
from psycopg.rows import dict_row

app = Flask(__name__)
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://dashboard:change-this-local-password@localhost:5432/performance",
)
SEED = [
    ("Engineering", 42, 91.4, 87.2, 12),
    ("Customer Support", 28, 88.1, 93.6, 8),
    ("Sales", 19, 84.7, 78.9, 15),
    ("Human Resources", 11, 95.2, 89.1, 4),
    ("Operations", 24, 90.3, 86.5, 9),
]


def connect():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def initialize_database():
    for attempt in range(30):
        try:
            with connect() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS department_metrics (
                        id SERIAL PRIMARY KEY,
                        department TEXT UNIQUE NOT NULL,
                        employees INTEGER NOT NULL,
                        target_pct NUMERIC(5,1) NOT NULL,
                        satisfaction_pct NUMERIC(5,1) NOT NULL,
                        open_roles INTEGER NOT NULL
                    )
                """)
                conn.cursor().executemany(
                    """INSERT INTO department_metrics
                       (department, employees, target_pct, satisfaction_pct, open_roles)
                       VALUES (%s, %s, %s, %s, %s)
                       ON CONFLICT (department) DO NOTHING""",
                    SEED,
                )
            return
        except psycopg.OperationalError:
            if attempt == 29:
                raise
            time.sleep(2)


@app.get("/health")
def health():
    try:
        with connect() as conn:
            conn.execute("SELECT 1")
        return jsonify(status="ok", database="connected")
    except psycopg.Error:
        return jsonify(status="error", database="unavailable"), 503


@app.get("/api/departments")
def departments():
    with connect() as conn:
        rows = conn.execute(
            "SELECT department, employees, target_pct, satisfaction_pct, open_roles "
            "FROM department_metrics ORDER BY department"
        ).fetchall()
    return jsonify(rows)


@app.get("/")
def dashboard():
    with connect() as conn:
        rows = conn.execute(
            "SELECT department, employees, target_pct, satisfaction_pct, open_roles "
            "FROM department_metrics ORDER BY department"
        ).fetchall()
    totals = {
        "employees": sum(r["employees"] for r in rows),
        "target": round(sum(float(r["target_pct"]) for r in rows) / len(rows), 1),
        "satisfaction": round(sum(float(r["satisfaction_pct"]) for r in rows) / len(rows), 1),
        "open_roles": sum(r["open_roles"] for r in rows),
    }
    return render_template_string(PAGE, rows=rows, totals=totals)


PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Department Performance</title><style>
*{box-sizing:border-box}body{margin:0;background:#f3f6fa;color:#17233c;font:15px system-ui,sans-serif}
header{background:#13294b;color:white;padding:26px max(24px,calc((100vw - 1100px)/2))}header small{color:#b9cbe4;letter-spacing:.12em;text-transform:uppercase}h1{margin:5px 0;font-size:27px}.wrap{max-width:1100px;margin:28px auto;padding:0 20px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px}.card,section{background:white;border:1px solid #e2e8f0;border-radius:12px;padding:20px}.label{color:#64748b;font-size:13px}.value{font-size:29px;font-weight:700;margin-top:5px}section{margin-top:20px;padding:0;overflow:auto}h2{font-size:18px;padding:18px 20px;margin:0;border-bottom:1px solid #e2e8f0}table{width:100%;border-collapse:collapse;min-width:620px}th,td{text-align:left;padding:13px 20px;border-bottom:1px solid #edf1f5}th{font-size:12px;text-transform:uppercase;color:#64748b}tr:last-child td{border:0}.pill{background:#e9f7ef;color:#197044;border-radius:99px;padding:4px 9px;font-weight:600;font-size:13px}footer{color:#64748b;font-size:12px;margin:14px 2px}
</style></head><body><header><small>People &amp; Operations</small><h1>Department Performance</h1><div>Team health and quarterly delivery snapshot</div></header><main class="wrap">
<div class="cards"><div class="card"><div class="label">Total employees</div><div class="value">{{ totals.employees }}</div></div><div class="card"><div class="label">Avg. target completion</div><div class="value">{{ totals.target }}%</div></div><div class="card"><div class="label">Avg. satisfaction</div><div class="value">{{ totals.satisfaction }}%</div></div><div class="card"><div class="label">Open roles</div><div class="value">{{ totals.open_roles }}</div></div></div>
<section><h2>Department breakdown</h2><table><thead><tr><th>Department</th><th>Employees</th><th>Target completion</th><th>Satisfaction</th><th>Open roles</th></tr></thead><tbody>
{% for r in rows %}<tr><td><strong>{{ r.department }}</strong></td><td>{{ r.employees }}</td><td><span class="pill">{{ r.target_pct }}%</span></td><td>{{ r.satisfaction_pct }}%</td><td>{{ r.open_roles }}</td></tr>{% endfor %}
</tbody></table></section><footer>Sample dashboard data for local deployment. Replace it with approved department metrics before production use.</footer></main></body></html>"""


if __name__ == "__main__":
    initialize_database()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
