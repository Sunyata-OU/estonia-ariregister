import sqlite3
import json
from pathlib import Path

db_path = Path("data/registry.db")
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
row = conn.execute("SELECT enrichment FROM companies WHERE code = 16631240").fetchone()
if row and row['enrichment']:
    print("Enrichment Data:")
    print(json.dumps(json.loads(row['enrichment']), indent=2))
else:
    print("No enrichment data found for 16631240")
conn.close()
