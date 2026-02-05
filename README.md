# Estonian Business Registry CLI

A high-performance, memory-efficient tool for downloading, merging, searching, and enriching the Estonian Business Registry open data.

## Features

- **Parallel & Incremental Downloads**: Fetches all registry files simultaneously. Skips files that haven't changed on the server.
- **SQLite Support (Optional)**: Migrate to a local database for 100x faster searches and more reliable enrichment.
- **Streaming Merge**: Processes large JSON files using streaming I/O to maintain a low memory footprint.
- **Advanced Search**: Filter by name, registry code, location (city/county), status, or even persons (ID/Name).
- **PDF Enrichment**: Automatically downloads and parses official Registry Card PDFs to extract management board details and personal IDs.
- **Exporting**: Save search results to JSON or CSV for external analysis.

## Prerequisites

- **Python 3.12+**
- **uv**: Recommended for dependency management.
- **jq** (Optional): Dramatically reduces RAM usage during the merge process.

## Installation

```bash
git clone https://github.com/your-repo/estonia-registry.git
cd estonia-registry
uv sync
```

## Usage

### 1. Synchronize Data
Downloads updates (if available) and merges them:
```bash
uv run registry.py sync
```

### 2. Search & Export
```bash
# Search for a person across all companies
uv run registry.py search -p "Tony Benoy"

# Filter by location and status, then export to CSV
uv run registry.py search -l "Harju" -s "Registrisse kantud" --export harju_companies.csv

# Search by code (instant jump via index)
uv run registry.py search -c 16631240

# Translate results to English
uv run registry.py search -n "Bolt" --translate
```

### 3. Enrichment
```bash
# Enrich specific companies (limit 10 per run)
uv run registry.py enrich 16631240
```

### 4. Statistics
```bash
uv run registry.py stats
```

## SDK Usage

You can also use the registry logic directly in your own Python code:

```python
from registry import EstonianRegistry

# Initialize the registry (defaults to 'data' directory)
reg = EstonianRegistry()

# Search for a company
results = reg.search(term="Bolt", translate=True)

for company in results:
    print(f"{company['name']} ({company['registry_code']})")
    print(f"Status: {company['status']}")

# Get analytics
stats = reg.get_analytics()
print(f"Total companies: {stats['total']}")
```

## Database Backend (Optional)
For much faster performance, you can use SQLite:
1. Initialize the database during merge:
   ```bash
   uv run registry.py merge --use-db
   ```
2. Subsequent commands will automatically detect `registry.db` and use it for instant searches.

## Data Structure
The tool creates a `chunks/` directory:
- `chunk_XXX.json`: Compressed company records.
- `manifest.json`: Index for instant lookups by registry code.

## License
MIT

## Disclaimer

**IMPORTANT: READ CAREFULLY.**

This software is provided "as is" and "with all faults," without any warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and non-infringement.

1.  **Compliance with RIK Terms:** By using this tool, you agree to comply with the [Terms of Use of the Estonian Business Registry (RIK) Open Data](https://ariregister.rik.ee/eng/open_data). You are solely responsible for ensuring that your use of the data (including automated downloading and parsing) adheres to their policies and rate limits.
2.  **No Liability:** In no event shall the authors, contributors, or copyright holders be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or in connection with the software or the use or other dealings in the software.
3.  **Data Accuracy:** This tool retrieves and parses public data from the Estonian Business Registry (RIK). The authors make no guarantees regarding the accuracy, completeness, or timeliness of the data provided by the registry or the parsing logic within this tool.
4.  **Use at Your Own Risk:** Users are solely responsible for any decisions made or actions taken based on the information provided by this tool. This software is not intended for use in high-stakes environments, legal compliance verification, or financial due diligence without independent verification.
5.  **No Official Affiliation:** This project is an independent tool and is not affiliated with, endorsed by, or sponsored by the Centre of Registers and Information Systems (RIK) or any Estonian government entity.

By using this software, you acknowledge that you have read this disclaimer, agree to its terms, and accept full responsibility for your use of the retrieved data.
