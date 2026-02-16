import sqlite3
import json
from pathlib import Path

db_path = Path("data/registry.db")
if not db_path.exists():
    print("Database not found")
else:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    count = conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
    print(f"Total companies: {count}")
    
    row = conn.execute("SELECT * FROM companies LIMIT 1").fetchone()
    if row:
        print("Sample Record:")
        print(dict(row))
        data = json.loads(row['full_data'])
        print("Keys in full_data:", list(data.keys()))
        for k in ['osanikud', 'isikud', 'kasusaajad']:
            if k in data:
                print(f"{k} type: {type(data[k])}")
                print(f"{k} value snippet: {str(data[k])[:100]}")
    conn.close()
