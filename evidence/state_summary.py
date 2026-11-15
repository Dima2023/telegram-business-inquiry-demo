"""Print a sanitized summary of a bot state file: counts and inquiry fields only.

Usage: python3 evidence/state_summary.py telegram-state.db

Chat IDs and message texts are never printed. The file is opened read-only.
"""
import json
import sqlite3
import sys


def summary(path: str) -> list[str]:
    db = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        updates = db.execute("select count(*) from updates").fetchone()[0]
        outbox = db.execute("select status, count(*) from outbox group by status order by status").fetchall()
        row = db.execute("select value from state").fetchone()
    finally:
        db.close()
    log = json.loads(row[0]).get("admin_log", []) if row else []
    lines = [f"updates processed: {updates}",
             "outbox by status: " + (", ".join(f"{status} {count}" for status, count in outbox) or "empty"),
             f"inquiries recorded: {len(log)}"]
    lines += [f"  id={item['id']} service={item['service']} quantity={item['quantity']} status={item['status']}"
              for item in log]
    return lines


if __name__ == "__main__":
    print("\n".join(summary(sys.argv[1])))
