#!/usr/bin/env python3
"""
Estonian Registry Data Merger

Unzips and merges Estonian business registry data files into a single JSON.
Files are merged by ariregistri_kood (registry code).
"""

import csv
import json
import zipfile
from pathlib import Path
from collections import defaultdict


def unzip_file(zip_path: Path, output_dir: Path) -> Path:
    """Unzip a file and return the path to the extracted file."""
    with zipfile.ZipFile(zip_path, 'r') as zf:
        names = zf.namelist()
        if not names:
            raise ValueError(f"Empty zip file: {zip_path}")
        zf.extractall(output_dir)
        return output_dir / names[0]


def load_json_file(file_path: Path) -> list:
    """Load a JSON file and return the data."""
    print(f"  Loading {file_path.name}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_csv_file(file_path: Path) -> list:
    """Load a CSV file (semicolon-separated) and return as list of dicts."""
    print(f"  Loading {file_path.name}...")
    data = []
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            # Convert ariregistri_kood to int for consistency
            if 'ariregistri_kood' in row:
                try:
                    row['ariregistri_kood'] = int(row['ariregistri_kood'])
                except (ValueError, TypeError):
                    pass
            data.append(row)
    return data


def merge_data(base_data: dict, json_data: list, key_name: str) -> None:
    """
    Merge JSON data into base_data dictionary.
    json_data is a list of objects with ariregistri_kood and other fields.
    """
    for item in json_data:
        reg_code = item.get('ariregistri_kood')
        if reg_code is None:
            continue

        if reg_code not in base_data:
            base_data[reg_code] = {
                'ariregistri_kood': reg_code,
                'nimi': item.get('nimi', '')
            }

        # Add all fields from this dataset except the common ones
        for field, value in item.items():
            if field not in ('ariregistri_kood', 'nimi'):
                base_data[reg_code][key_name + '_' + field if key_name else field] = value


def main():
    base_dir = Path(__file__).parent
    output_dir = base_dir / 'extracted'
    output_dir.mkdir(exist_ok=True)

    # Define the zip files and their types
    zip_files = {
        'lihtandmed': ('ettevotja_rekvisiidid__lihtandmed.csv.zip', 'csv'),
        'yldandmed': ('ettevotja_rekvisiidid__yldandmed.json.zip', 'json'),
        'osanikud': ('ettevotja_rekvisiidid__osanikud.json.zip', 'json'),
        'kasusaajad': ('ettevotja_rekvisiidid__kasusaajad.json.zip', 'json'),
        'kaardile_kantud_isikud': ('ettevotja_rekvisiidid__kaardile_kantud_isikud.json.zip', 'json'),
        'registrikaardid': ('ettevotja_rekvisiidid__registrikaardid.json.zip', 'json'),
    }

    # Step 1: Unzip all files
    print("Step 1: Unzipping files...")
    extracted_files = {}
    for name, (zip_name, file_type) in zip_files.items():
        zip_path = base_dir / zip_name
        if zip_path.exists():
            print(f"  Unzipping {zip_name}...")
            extracted_files[name] = (unzip_file(zip_path, output_dir), file_type)
        else:
            print(f"  Warning: {zip_name} not found, skipping...")

    # Step 2: Load and merge data
    print("\nStep 2: Loading and merging data...")

    # Use lihtandmed (basic data) as the base since it's CSV with core company info
    merged_data = {}

    # Load CSV base data first
    if 'lihtandmed' in extracted_files:
        file_path, _ = extracted_files['lihtandmed']
        csv_data = load_csv_file(file_path)
        for row in csv_data:
            reg_code = row.get('ariregistri_kood')
            if reg_code:
                merged_data[reg_code] = row
        print(f"  Loaded {len(merged_data)} companies from lihtandmed")

    # Process each JSON file
    json_field_mapping = {
        'yldandmed': None,  # Fields go directly (general data)
        'osanikud': 'osanikud',  # Shareholders
        'kasusaajad': 'kasusaajad',  # Beneficiaries
        'kaardile_kantud_isikud': 'kaardile_kantud_isikud',  # Registered persons
        'registrikaardid': 'registrikaardid',  # Register cards
    }

    for name, key_prefix in json_field_mapping.items():
        if name not in extracted_files:
            continue

        file_path, _ = extracted_files[name]
        json_data = load_json_file(file_path)
        print(f"  Processing {len(json_data)} records from {name}...")

        for item in json_data:
            reg_code = item.get('ariregistri_kood')
            if reg_code is None:
                continue

            if reg_code not in merged_data:
                merged_data[reg_code] = {
                    'ariregistri_kood': reg_code,
                    'nimi': item.get('nimi', '')
                }

            # For yldandmed, merge fields directly (except ariregistri_kood and nimi)
            if key_prefix is None:
                for field, value in item.items():
                    if field not in ('ariregistri_kood', 'nimi'):
                        merged_data[reg_code][field] = value
            else:
                # For other files, collect records into an array under the key
                nested_record = {
                    field: value for field, value in item.items()
                    if field not in ('ariregistri_kood', 'nimi')
                }
                if key_prefix not in merged_data[reg_code]:
                    merged_data[reg_code][key_prefix] = []
                merged_data[reg_code][key_prefix].append(nested_record)

    # Step 3: Convert to list and save
    print("\nStep 3: Saving merged data...")
    merged_list = list(merged_data.values())

    # Sort by registry code for consistency
    merged_list.sort(key=lambda x: x.get('ariregistri_kood', 0))

    output_file = base_dir / 'merged_registry.json'
    print(f"  Writing {len(merged_list)} companies to {output_file.name}...")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_list, f, ensure_ascii=False, indent=2)

    print(f"\nDone! Merged data saved to: {output_file}")
    print(f"Total companies: {len(merged_list)}")

    # Cleanup extracted files (optional)
    cleanup = input("\nDelete extracted files? (y/n): ").strip().lower()
    if cleanup == 'y':
        import shutil
        shutil.rmtree(output_dir)
        print("Extracted files deleted.")


if __name__ == '__main__':
    main()
