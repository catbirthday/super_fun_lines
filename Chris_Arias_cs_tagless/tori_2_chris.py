#!/usr/bin/env python3
import re
import glob
import os

BASE_DIR = "/workspace/super_fun_lines/fun_lines/Chris_Arias_cs_tagless"
OFFSET = 612
START_FILE = 8

def add_offset_to_numbers(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    def add_offset(match):
        num = int(match.group(1))
        return str(num + OFFSET) + match.group(2)
    
    # Match number at start of line followed by space
    new_content = re.sub(r'^(\d+)(\s)', add_offset, content, flags=re.MULTILINE)
    
    with open(filepath, 'w') as f:
        f.write(new_content)
    
    print(f"Processed: {filepath}")

def main():
    pattern = os.path.join(BASE_DIR, "actor_assignments*.txt")
    files = glob.glob(pattern)
    
    for filepath in sorted(files):
        # Extract file number
        match = re.search(r'actor_assignments(\d+)\.txt', filepath)
        if match:
            file_num = int(match.group(1))
            if file_num >= START_FILE:
                add_offset_to_numbers(filepath)

if __name__ == "__main__":
    main()