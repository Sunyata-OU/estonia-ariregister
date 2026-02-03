import json
import sys

def view_json_head(file_path, batch_size=10):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Skip the opening '['
            char = f.read(1)
            while char and char != '[':
                char = f.read(1)
            
            decoder = json.JSONDecoder()
            buffer = ""
            
            while True:
                objects_shown_in_batch = 0
                eof_reached = False
                
                while objects_shown_in_batch < batch_size:
                    # Try to decode from current buffer
                    buffer = buffer.lstrip()
                    if buffer.startswith(','):
                        buffer = buffer[1:].lstrip()
                    
                    try:
                        if buffer:
                            obj, index = decoder.raw_decode(buffer)
                            print(json.dumps(obj, indent=2, ensure_ascii=False))
                            print("-" * 40)
                            objects_shown_in_batch += 1
                            buffer = buffer[index:]
                            continue
                    except json.JSONDecodeError:
                        pass
                    
                    # Read more data if we couldn't decode or need more
                    chunk = f.read(4096)
                    if not chunk:
                        eof_reached = True
                        break
                    buffer += chunk
                
                if objects_shown_in_batch == 0 and eof_reached:
                    print("No more objects found.")
                    break
                
                if eof_reached:
                    print("End of file reached.")
                    break

                try:
                    choice = input(f"Show next {batch_size}? (y/n): ").strip().lower()
                except EOFError:
                    break
                    
                if choice != 'y':
                    break

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    file_to_read = 'merged_registry.json'
    view_json_head(file_to_read)
