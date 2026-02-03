#!/usr/bin/env python3
"""
Search for a company in the merged registry JSON file.
Usage: python3 search_registry.py <search_term>
"""

import sys
import json

def search_registry(file_path, search_term):
    print(f"Searching for '{search_term}' in {file_path}...")
    
    is_code = search_term.isdigit()
    search_term_lower = search_term.lower()
    
    found_count = 0
    current_obj_lines = []
    in_object = False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                # ... (rest of loop logic remains same until print)
                if line.startswith('  {'):
                    in_object = True
                    current_obj_lines = [line]
                
                elif in_object:
                    current_obj_lines.append(line)
                    
                    stripped_right = line.rstrip()
                    
                    if stripped_right == '  },' or stripped_right == '  }':
                        obj_str = "".join(current_obj_lines)
                        clean_str = obj_str.strip()
                        if clean_str.endswith(','):
                            clean_str = clean_str[:-1]
                            
                        try:
                            if search_term_lower in clean_str.lower():
                                data = json.loads(clean_str)
                                
                                match = False
                                if is_code:
                                    if str(data.get('ariregistri_kood')) == search_term:
                                        match = True
                                else:
                                    if search_term_lower in data.get('nimi', '').lower():
                                        match = True
                                
                                if match:
                                    try:
                                        print("-" * 40)
                                        print(json.dumps(data, indent=2, ensure_ascii=False))
                                    except BrokenPipeError:
                                        sys.exit(0)
                                        
                                    found_count += 1
                                    if is_code:
                                        return 
                            
                        except json.JSONDecodeError:
                            pass
                        
                        in_object = False
                        current_obj_lines = []

    except KeyboardInterrupt:
        print("\nInterrupted.")
    except BrokenPipeError:
        sys.exit(0)
    
    if found_count == 0:
        print("No results found.")
    else:
        print(f"Found {found_count} match(es).")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 search_registry.py <search_term>")
        sys.exit(1)
    
    term = " ".join(sys.argv[1:])
    search_registry('merged_registry.json', term)
