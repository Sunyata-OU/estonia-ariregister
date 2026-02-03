#!/usr/bin/env python3
"""
Fast search for a company in the merged registry JSON file using memory mapping.
Usage: python3 search_registry_fast.py <search_term>
"""

import sys
import json
import mmap
import os

def search_registry_fast(file_path, search_term):
    print(f"Searching for '{search_term}' in {file_path}...")
    
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return

    is_code = search_term.isdigit()
    search_term_bytes = search_term.encode('utf-8')
    search_term_lower_bytes = search_term.lower().encode('utf-8')
    
    # Pre-calculate markers for structure (assuming indent=2 from merge script)
    # Top-level objects start with "\n  {" and end with "\n  }," or "\n  }"
    # We use byte literals for speed
    START_MARKER = b'\n  {'
    END_MARKER_COMMA = b'\n  },'
    END_MARKER_LAST = b'\n  }'
    
    found_count = 0
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Memory map the file
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                
                # If searching for a code, we can optimize further by looking for the specific key
                # "ariregistri_kood": 12345678
                if is_code:
                    # Note: formatting matches standard json.dump (key": value)
                    # We try exact format first
                    key_search = b'"ariregistri_kood": ' + search_term_bytes
                    cursor = 0
                    
                    while True:
                        # Find the specific key-value pair
                        idx = mm.find(key_search, cursor)
                        if idx == -1:
                            # Fallback: simple search if strict formatting fails
                            # (But usually not needed for generated files)
                            if cursor == 0: 
                                # If we didn't find any strict match, try loose search
                                break 
                            break
                        
                        # We found the code. Now expand to find the containing object.
                        # Scan backwards for the start of the object
                        start_pos = mm.rfind(START_MARKER, 0, idx)
                        if start_pos == -1:
                            # Might be the very first object "[ \n  {"
                            # Check if the file starts with marker (ignoring [)
                            pass 
                        
                        # Adjust to include the whitespace/brace
                        # rfind returns index of \n. We want to include \n? 
                        # usually json.loads doesn't care about leading whitespace.
                        # Let's start from start_pos + 1 (the space)
                        obj_start = start_pos + 1
                        
                        # Scan forward for the end of the object
                        end_pos = mm.find(END_MARKER_COMMA, idx)
                        if end_pos == -1:
                            # Try the last item marker
                            end_pos = mm.find(END_MARKER_LAST, idx)
                        
                        if end_pos != -1:
                            # Include the closing brace: "\n  }" len is 4.
                            # We want up to '}'
                            # If found "\n  },\", end_pos points to \n.
                            # We want to read up to '}'
                            # Let's read a safe chunk and let logic trim it
                            # Actually, simpler: find the '}'
                            brace_pos = mm.find(b'}', end_pos)
                            obj_end = brace_pos + 1
                            
                            obj_bytes = mm[obj_start:obj_end]
                            
                            try:
                                data = json.loads(obj_bytes)
                                print("-" * 40)
                                print(json.dumps(data, indent=2, ensure_ascii=False))
                                found_count += 1
                                return # Exact code match found, we are done
                            except json.JSONDecodeError:
                                pass
                        
                        cursor = idx + 1

                # If we are here, either it's not a code, or strict code search failed
                # Do a general text search
                cursor = 0
                while True:
                    idx = mm.find(search_term_lower_bytes, cursor)
                    if idx == -1:
                        break
                    
                    # Found a text match. Find the containing object.
                    # 1. Find start of object (backwards)
                    start_pos = mm.rfind(START_MARKER, 0, idx)
                    if start_pos == -1:
                        # Check if it is the first object
                        if idx < 5000: # Arbitrary small header size
                            # Check if we have a start brace before
                            first_brace = mm.rfind(b'{', 0, idx)
                            if first_brace != -1:
                                # Verify indentation?
                                # Assume it's valid if it's near start
                                start_pos = first_brace - 3 # adjust fake marker
                                obj_start = first_brace
                            else:
                                cursor = idx + 1
                                continue
                        else:
                            cursor = idx + 1
                            continue
                    else:
                        obj_start = start_pos + 1

                    # 2. Find end of object (forwards)
                    # We start searching for end AFTER the text match
                    end_pos_comma = mm.find(END_MARKER_COMMA, idx)
                    end_pos_last = mm.find(END_MARKER_LAST, idx)
                    
                    end_pos = -1
                    if end_pos_comma != -1 and end_pos_last != -1:
                        end_pos = min(end_pos_comma, end_pos_last)
                    elif end_pos_comma != -1:
                        end_pos = end_pos_comma
                    elif end_pos_last != -1:
                        end_pos = end_pos_last
                    
                    if end_pos != -1:
                        # Find the actual '}'
                        brace_pos = mm.find(b'}', end_pos)
                        obj_end = brace_pos + 1
                        
                        obj_bytes = mm[obj_start:obj_end]
                        
                        try:
                            # Verify valid JSON
                            data = json.loads(obj_bytes)
                            
                            # Verify the match is real (not just a substring in a hash)
                            match = False
                            
                            # Re-verify logic in Python on the object
                            # (Since mmap find matches raw bytes, it might match keys, values, anything)
                            json_str = json.dumps(data, ensure_ascii=False).lower()
                            if search_term.lower() in json_str:
                                match = True
                            
                            if match:
                                try:
                                    print("-" * 40)
                                    print(json.dumps(data, indent=2, ensure_ascii=False))
                                except BrokenPipeError:
                                    sys.exit(0)
                                found_count += 1
                                
                                # Move cursor to END of this object to avoid finding the same keyword 
                                # multiple times in the same object
                                cursor = end_pos + 1
                                continue

                        except json.JSONDecodeError:
                            pass
                    
                    # If we failed to parse or find boundaries, move past the current match
                    cursor = idx + 1

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
        print("Usage: python3 search_registry_fast.py <search_term>")
        sys.exit(1)
    
    term = " ".join(sys.argv[1:])
    search_registry_fast('merged_registry.json', term)
