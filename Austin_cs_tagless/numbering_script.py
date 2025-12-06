#!/usr/bin/env python3
"""
Austin.py - Process actor assignment files into numbered lines.

Reads all actor_assignments*.txt files from input directory and outputs
a single file with numbered lines, removing role prefixes and metadata
while keeping direction tags like [apologetically].

Handles three formats:
1. MONOLOGUE (dash style): --- MONOLOGUE --- with multi-line content
2. MONOLOGUE (equals style): === ITEM N - MONOLOGUE === with multi-line content  
3. BASIC SCENARIO: === ITEM N - BASIC SCENARIO === with single-line content
"""

import re
import os
import glob

input_dir = "/workspace/fun_lines/Austin_V3"
input_files = sorted(glob.glob(os.path.join(input_dir, "actor_assignments*.txt")))
output_file = "/workspace/fun_lines/Austin_V3/all_lines_numbered.txt"


def clean_text(text):
    """Remove all metadata, role prefixes, and instructions while keeping direction tags intact."""
    # "Character N:" style labels (anywhere in text)
    text = re.sub(r'Character\s*\d+:\s*', '', text)
    # "Role Name: D#:" or "Role Name: A#:" style (e.g., "Customer Support: D2:")
    text = re.sub(r'[A-Z][A-Za-z\s]+:\s*[A-Z]?\d+:\s*', '', text)
    # Simple role names at start of text only (e.g., "Narrator:")
    text = re.sub(r'^[A-Z][A-Za-z\s]+:\s*', '', text)
    
    # Truncate at first appearance of any metadata marker
    markers = [
        'ITEMS ',
        'ITEM ',
        'You are B;',
        'You are A;',
        'You are Character',
        'You are playing a customer service agent',
    ]
    for marker in markers:
        idx = text.find(marker)
        if idx != -1:
            text = text[:idx]
    
    # Clean up any leftover section markers
    text = re.sub(r'\s*={5,}\s*', ' ', text)
    text = re.sub(r'\s*-{5,}\s*', ' ', text)
    
    # Clean up extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def process_files():
    all_entries = []
    
    for filepath in input_files:
        if not os.path.exists(filepath):
            print(f"Warning: {filepath} not found, skipping")
            continue
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Normalize line endings (handle Windows CRLF)
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        
        # FORMAT 1: --- MONOLOGUE ---
        # --- MONOLOGUE... ---
        # This must be read out in a single delivery as one file (optional)
        # NUMBER SCENARIO: description
        # ==================================================
        # [multi-line content]
        monologue_pattern1 = r'---\s*MONOLOGUE[^\n]*---\s*\n(?:\s*[^\d\n][^\n]*\n)?\s*(\d+)\s+SCENARIO:[^\n]*\n=+\n(.*?)(?=\n---|\n\n\d+\s|\Z)'
        
        # FORMAT 2: === ITEM N - MONOLOGUE ===
        # ============================================================
        # ITEM 481 - MONOLOGUE SELFTALK (202 words)
        # Source: 00348d6d
        # ============================================================
        # This must be read out in a single delivery as one file
        # 481 SCENARIO: description
        # ==================================================
        # [multi-line content]
        monologue_pattern2 = r'={10,}\nITEM\s+(\d+)\s*-\s*MONOLOGUE[^\n]*\nSource:[^\n]*\n={10,}\n.*?\d+\s+SCENARIO:[^\n]*\n=+\n(.*?)(?=\n+={10,}\nITEM|\n---|\Z)'
        
        # FORMAT 3: Standalone NUM SCENARIO: (fallback for any missed monologues)
        scenario_pattern = r'(?<!\n)(\d+)\s+SCENARIO:[^\n]*\n=+\n(.*?)(?=\n---|\n\n\d+\s|\n={10,}\nITEM|\Z)'
        
        # Extract monologues with pattern 1
        for match in re.finditer(monologue_pattern1, content, re.DOTALL):
            line_num = int(match.group(1))
            monologue_text = ' '.join(match.group(2).strip().split())
            all_entries.append((line_num, monologue_text))
        
        # Extract monologues with pattern 2
        for match in re.finditer(monologue_pattern2, content, re.DOTALL):
            line_num = int(match.group(1))
            monologue_text = ' '.join(match.group(2).strip().split())
            all_entries.append((line_num, monologue_text))
        
        # Extract monologues with standalone SCENARIO pattern (fallback)
        for match in re.finditer(scenario_pattern, content, re.DOTALL):
            line_num = int(match.group(1))
            if line_num not in [e[0] for e in all_entries]:  # Avoid duplicates
                monologue_text = ' '.join(match.group(2).strip().split())
                all_entries.append((line_num, monologue_text))
        
        # Remove monologue sections for regular line processing
        content_cleaned = re.sub(monologue_pattern1, '\n', content, flags=re.DOTALL)
        content_cleaned = re.sub(monologue_pattern2, '\n', content_cleaned, flags=re.DOTALL)
        content_cleaned = re.sub(scenario_pattern, '\n', content_cleaned, flags=re.DOTALL)
        
        # Remove header/metadata lines - allow leading whitespace
        content_cleaned = re.sub(r'---[^\n]*---', '', content_cleaned)
        content_cleaned = re.sub(r'^\s*=+\s*$', '', content_cleaned, flags=re.MULTILINE)
        content_cleaned = re.sub(r'^\s*\d+\s+SCENARIO:[^\n]*$', '', content_cleaned, flags=re.MULTILINE)
        content_cleaned = re.sub(r'^\s*Script:[^\n]*$', '', content_cleaned, flags=re.MULTILINE)
        # Remove Character N: lines (other character's dialogue) - replace with marker
        content_cleaned = re.sub(r'^\s*Character\s*\d+:[^\n]*$', '###BREAK###', content_cleaned, flags=re.MULTILINE)
        # Remove ITEM/ITEMS headers - permissive patterns with optional leading whitespace
        content_cleaned = re.sub(r'^\s*ITEM\s+\d+[^\n]*$', '###BREAK###', content_cleaned, flags=re.MULTILINE)
        content_cleaned = re.sub(r'^\s*ITEMS\s+\d+-\d+[^\n]*$', '###BREAK###', content_cleaned, flags=re.MULTILINE)
        content_cleaned = re.sub(r'^\s*Source:[^\n]*$', '', content_cleaned, flags=re.MULTILINE)
        content_cleaned = re.sub(r'^\s*This must be read[^\n]*$', '', content_cleaned, flags=re.MULTILINE)
        # Remove instruction lines
        content_cleaned = re.sub(r'^\s*You are playing[^\n]*$', '###BREAK###', content_cleaned, flags=re.MULTILINE)
        content_cleaned = re.sub(r'^\s*You are [A-Z];[^\n]*$', '###BREAK###', content_cleaned, flags=re.MULTILINE)
        content_cleaned = re.sub(r'^\s*You are Character[^\n]*$', '###BREAK###', content_cleaned, flags=re.MULTILINE)
        
        # Process regular numbered lines
        lines = content_cleaned.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i]
            num_match = re.match(r'^(\d+)\s+(.*)$', line)
            
            if num_match:
                line_num = int(num_match.group(1))
                text_parts = [num_match.group(2)]
                
                # Gather continuation lines
                i += 1
                while i < len(lines):
                    next_line = lines[i]
                    next_stripped = next_line.strip()
                    
                    # Stop at break markers
                    if next_stripped == '###BREAK###':
                        i += 1
                        break
                    
                    # Stop at empty lines (indicates section break or removed content)
                    if not next_stripped:
                        i += 1
                        break
                    
                    # Stop at new numbered line or section markers
                    if (re.match(r'^\d+\s+', next_line) or 
                        next_line.startswith('---') or
                        next_stripped.startswith('===') or
                        next_stripped.startswith('ITEM ') or
                        next_stripped.startswith('ITEMS ') or
                        next_stripped.startswith('Source:') or
                        next_stripped.startswith('Script:') or
                        next_stripped.startswith('Character ') or
                        next_stripped.startswith('This must be read') or
                        next_stripped.startswith('You are')):
                        break
                    
                    text_parts.append(next_stripped)
                    i += 1
                
                full_text = ' '.join(text_parts)
                if full_text.strip():
                    all_entries.append((line_num, full_text))
            else:
                i += 1
    
    # Sort by line number and deduplicate
    all_entries.sort(key=lambda x: x[0])
    seen = set()
    unique_entries = []
    for num, text in all_entries:
        if num not in seen:
            seen.add(num)
            unique_entries.append((num, text))
    
    # Clean and format output - apply all cleanup AFTER joining
    output_lines = []
    for num, text in unique_entries:
        cleaned = clean_text(text)
        if cleaned:  # Only add if there's content after cleaning
            output_lines.append(f"{num}  {cleaned}")
    
    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
    
    print(f"Processed {len(output_lines)} lines to {output_file}")


if __name__ == "__main__":
    process_files()
