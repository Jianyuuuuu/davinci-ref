#!/usr/bin/env python3
"""
Extract text from DaVinci Resolve PDF manuals and save as Markdown.
Usage: python3 extract_md.py <pdf_path> <output_md_path>
"""
import sys
import fitz
import re
import time

def clean_text(text):
    """Clean extracted text for better Markdown readability."""
    # Remove excessive blank lines (more than 2 consecutive)
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Remove leading/trailing whitespace from lines
    lines = [line.rstrip() for line in text.split('\n')]
    # Remove lines that are only whitespace
    lines = [line for line in lines if line.strip()]
    return '\n'.join(lines)

def extract_pdf_to_md(pdf_path, output_path, verbose=True):
    """Extract all text from PDF and save as Markdown."""
    if verbose:
        print(f"Opening: {pdf_path}")
    
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    if verbose:
        print(f"Total pages: {total_pages}")
    
    all_text = []
    start_time = time.time()
    
    for page_num in range(total_pages):
        page = doc[page_num]
        text = page.get_text()
        text = clean_text(text)
        
        if text.strip():
            all_text.append(f"## Page {page_num + 1}\n\n{text}")
        
        # Progress update every 100 pages
        if (page_num + 1) % 100 == 0:
            elapsed = time.time() - start_time
            rate = (page_num + 1) / elapsed
            remaining = (total_pages - page_num - 1) / rate if rate > 0 else 0
            if verbose:
                print(f"  Page {page_num + 1}/{total_pages} | {rate:.1f} pages/sec | ETA: {remaining/60:.1f} min")
    
    doc.close()
    
    # Write output
    full_text = '\n\n'.join(all_text)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# {pdf_path.split('/')[-1]}\n\n")
        f.write(f"Extracted from: {pdf_path}\n\n")
        f.write(full_text)
    
    elapsed = time.time() - start_time
    if verbose:
        print(f"\nDone! Extracted {total_pages} pages in {elapsed/60:.1f} minutes")
        print(f"Output: {output_path}")
        print(f"File size: {len(full_text) / 1024 / 1024:.1f} MB")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 extract_md.py <pdf_path> <output_md_path>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_path = sys.argv[2]
    extract_pdf_to_md(pdf_path, output_path)
