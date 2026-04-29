#!/usr/bin/env python3
"""
Clean up DaVinci Resolve manual Markdown:
1. Keep ## Page N markers
2. Remove page header words (INTRO, MEDIA, CUT, etc.)
3. Remove standalone page numbers
4. Remove chapter footers
5. Remove TOC dot leaders
6. Normalize whitespace
"""
import re
import sys

def clean_page_content(lines):
    """Clean a single page's content, returning list of cleaned lines."""
    cleaned = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines
        if not line:
            i += 1
            continue
        
        # Skip standalone page number lines (just a number)
        if re.match(r'^\d+$', line):
            i += 1
            continue
        
        # Skip header words
        if re.match(r'^(INTRO|MEDIA|CUT|EDIT|FUSION|COLOR|FAIRLIGHT|DELIVER|CLOUD|COLLAB|IMMERSIVE|OTHER|MENU|CONTENTS)$', line):
            i += 1
            continue
        
        # Skip chapter footer pattern
        if re.match(r'^DaVinci Resolve Interface\s*\|\s*Chapter', line):
            i += 1
            continue
        
        # Skip TOC dot leaders
        if re.match(r'^.+?\.{3,}\s*[\d‑-]+\s*$', line):
            i += 1
            continue
        
        # Skip lines that are just "Chapter N" repeated (page section titles in TOC)
        if re.match(r'^Chapter \d+$', line) and i + 1 < len(lines) and not lines[i + 1].strip():
            i += 1
            continue
        
        cleaned.append(lines[i])
        i += 1
    
    return cleaned

def clean_text(text):
    # Split into pages by "## Page N" header (keep delimiter)
    parts = re.split(r'(## Page \d+)', text)
    
    cleaned_parts = []
    # parts are [intro_text, "## Page N", page1_text, "## Page N", page2_text, ...]
    i = 0
    while i < len(parts):
        if re.match(r'## Page \d+', parts[i]):
            # This is a page header
            cleaned_parts.append(parts[i])
            i += 1
            if i < len(parts):
                # Clean the page content
                lines = parts[i].split('\n')
                cleaned_lines = clean_page_content(lines)
                if cleaned_lines:
                    cleaned_parts.append('\n'.join(cleaned_lines))
        else:
            # Intro text before first page - keep as-is but clean TOC dot leaders
            intro = parts[i]
            intro = re.sub(r'^.+?\.{3,}\s*[\d‑-]+\s*$\n?', '', intro, flags=re.MULTILINE)
            if intro.strip():
                cleaned_parts.append(intro)
        i += 1
    
    # Join and normalize blank lines
    result = '\n'.join(cleaned_parts)
    result = re.sub(r'\n{4,}', '\n\n', result)
    
    return result.strip() + '\n'

def process_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    cleaned = clean_text(text)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(cleaned)
    
    original_size = len(text)
    cleaned_size = len(cleaned)
    print(f"Cleaned: {input_path}")
    print(f"  Original: {original_size/1024:.1f} KB")
    print(f"  Cleaned:  {cleaned_size/1024:.1f} KB")
    print(f"  Removed:  {(original_size - cleaned_size)/1024:.1f} KB ({(original_size - cleaned_size)/original_size*100:.1f}%)")
    print(f"  Output:   {output_path}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 clean_md.py <input_path> <output_path>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    process_file(input_path, output_path)
