#!/usr/bin/env python3
import urllib.request
from pathlib import Path

BASE_URL = "https://avaandmed.ariregister.rik.ee/sites/default/files/avaandmed/"
DATA_FILES = {
    "ettevotja_rekvisiidid__yldandmed.json.zip": "ettevotja_rekvisiidid__yldandmed.json.zip",
    "ettevotja_rekvisiidid__osanikud.json.zip": "ettevotja_rekvisiidid__osanikud.json.zip",
    "ettevotja_rekvisiidid__kasusaajad.json.zip": "ettevotja_rekvisiidid__kasusaajad.json.zip",
    "ettevotja_rekvisiidid__kaardile_kantud_isikud.json.zip": "ettevotja_rekvisiidid__kaardile_kantud_isikud.json.zip",
    "ettevotja_rekvisiidid__registrikaardid.json.zip": "ettevotja_rekvisiidid__registrikaardid.json.zip",
    "ettevotja_rekvisiidid__lihtandmed.csv.zip": "ettevotja_rekvisiidid__lihtandmed.csv.zip",
}

def download_file(url, filename):
    print(f"Downloading {filename} from {url}...")
    try:
        # User-agent might be needed to avoid 403
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        )
        with urllib.request.urlopen(req) as response, open(filename, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
        print(f"Successfully downloaded {filename}")
    except Exception as e:
        print(f"Error downloading {filename}: {e}")

def main():
    base_dir = Path(__file__).parent
    for filename, relative_url in DATA_FILES.items():
        url = BASE_URL + relative_url
        output_path = base_dir / filename
        # Only download if not exists
        if not output_path.exists():
            download_file(url, output_path)
        else:
            print(f"File {filename} already exists, skipping. Delete it to redownload.")

if __name__ == "__main__":
    main()