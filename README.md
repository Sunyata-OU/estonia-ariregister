# Estonia Business Registry Tools

This project contains tools to merge and search the Estonian Business Registry Open Data.

## Scripts

### 0. `download_data.py`
Automates the downloading of the latest raw data files from the Estonian Business Register.
- **Source:** [e-Business Register Open Data](https://avaandmed.ariregister.rik.ee/en/downloading-open-data)
- **Usage:**
  ```bash
  python3 download_data.py
  ```

### 1. `merge_registry.py`
Merges the individual raw data files (ZIP archives) provided by the business registry into a single, unified JSON file (`merged_registry.json`).
- **Input:** Zip files in the root directory (e.g., `ettevotja_rekvisiidid__yldandmed.json.zip`).
- **Output:** `merged_registry.json` (approx. 5-6 GB).
- **Usage:**
  ```bash
  python3 merge_registry.py
  ```

### 2. `search_registry_fast.py` (Recommended)
A high-performance search tool that uses **memory mapping** to instantly search the large `merged_registry.json` file without loading it entirely into RAM.
- **Features:**
  - Instant lookup by Registry Code.
  - Fast free-text search by Company Name.
  - Low memory usage.
- **Usage:**
  ```bash
  # Search by Registry Code
  python3 search_registry_fast.py 10000018

  # Search by Name
  python3 search_registry_fast.py "Amserv Auto"
  ```

### 3. `search_registry.py` (Legacy)
A slower, streaming-based search implementation. Useful if memory mapping is not supported on your system or for debugging.
- **Usage:**
  ```bash
  python3 search_registry.py "Search Term"
  ```

### 4. `view_head.py`
An interactive utility to view the first few records of `merged_registry.json`. It decodes and pretty-prints JSON objects in batches, asking the user if they want to see more.
- **Usage:**
  ```bash
  python3 view_head.py
  ```

## Data Source
The data is sourced from the Estonian Business Register (e-Business Register) open data.
Expected input files:
- `ettevotja_rekvisiidid__yldandmed.json.zip`
- `ettevotja_rekvisiidid__osanikud.json.zip`
- `ettevotja_rekvisiidid__kasusaajad.json.zip`
- `ettevotja_rekvisiidid__kaardile_kantud_isikud.json.zip`
- `ettevotja_rekvisiidid__registrikaardid.json.zip`
- `ettevotja_rekvisiidid__lihtandmed.csv.zip`

## Requirements
- Python 3.6+
- No external dependencies (uses standard library `json`, `mmap`, `csv`, `zipfile`).
