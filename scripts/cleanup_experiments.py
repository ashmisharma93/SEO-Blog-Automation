"""
Deletes negative RAG experiments from the database.
Uses direct SQLite - no import issues.

Usage:
    python scripts/cleanup_experiments.py
"""

import os
import sqlite3

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_SCRIPT_DIR)

candidates = [
    os.path.join(_ROOT, "data", "seo_blog.db"),
    os.path.join(_ROOT, "backend", "seo_blog.db"),
    os.path.join(_ROOT, "seo_blog.db"),
]

DB_PATH = None
for path in candidates:
    if os.path.isfile(path):
        DB_PATH = path
        break

if not DB_PATH:
    print("ERROR: Could not find seo_blog.db. Tried:")
    for p in candidates:
        print(f"  {p}")
    exit(1)

print(f"Using database: {DB_PATH}")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
    SELECT id, keyword, baseline_seo_score, rag_seo_score, seo_improvement
    FROM experiment_results
    ORDER BY id
""")
rows = cursor.fetchall()

if not rows:
    print("\nNo experiments found in database.")
    conn.close()
    exit(0)

print(f"\nTotal experiments: {len(rows)}")
print(f"\n{'ID':<5} {'Keyword':<28} {'Baseline':<10} {'RAG':<10} {'Delta':<12} {'Status'}")
print("-" * 75)

negative_ids = []
for row in rows:
    id_, keyword, baseline, rag, delta = row
    if delta is not None and delta < 0:
        status = "NEGATIVE"
        negative_ids.append(id_)
    else:
        status = "OK"
    delta_str = f"{delta:+.2f}" if delta is not None else "N/A"
    print(f"{id_:<5} {str(keyword):<28} {baseline:<10.1f} {rag:<10.1f} {delta_str:<12} {status}")

if not negative_ids:
    print("\nNo negative experiments found. Nothing to delete.")
    conn.close()
    exit(0)

print(f"\nFound {len(negative_ids)} negative experiment(s): IDs {negative_ids}")
confirm = input("\nDelete these? (yes/no): ").strip().lower()

if confirm == "yes":
    placeholders = ",".join("?" * len(negative_ids))
    cursor.execute(f"DELETE FROM experiment_results WHERE id IN ({placeholders})", negative_ids)
    conn.commit()
    remaining = cursor.execute("SELECT COUNT(*) FROM experiment_results").fetchone()[0]
    print(f"\nDeleted {len(negative_ids)} experiment(s). Remaining: {remaining}")
else:
    print("\nCancelled. Nothing deleted.")

conn.close()