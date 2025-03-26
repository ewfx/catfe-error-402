#!/usr/bin/env python3
"""
Semantic Chunking Script for API Documentation
----------------------------------------------
This script parses structured HTML API documentation and splits it into semantic chunks for embedding.
It outputs a JSON array of chunk objects with 'id', 'title', 'content', and optional 'source'.
"""
import re
import json
import sys
import argparse
from bs4 import BeautifulSoup, NavigableString

def get_text_with_inline_formatting(element):
    """Recursively get text from an element, preserving inline code and line breaks."""
    parts = []
    for child in element.children:
        if isinstance(child, NavigableString):
            parts.append(str(child))
        elif child.name == 'code':
            # Wrap inline code in backticks
            parts.append(f"`{child.get_text()}`")
        elif child.name == 'br':
            # Line break
            parts.append("\n")
        else:
            # Recurse into other child elements
            parts.append(get_text_with_inline_formatting(child))
    return "".join(parts)

def render_elements_to_text(elements):
    """Convert a list of BeautifulSoup elements to formatted text with structure preserved."""
    parts = []
    for elem in elements:
        if isinstance(elem, NavigableString):
            text = str(elem)
            if text.strip():
                parts.append(text)
        elif elem.name:
            tag = elem.name
            if tag in ['p', 'div', 'span']:
                # Paragraph or generic block
                text = get_text_with_inline_formatting(elem).strip()
                if text:
                    parts.append(text)
                    parts.append("\n\n")
            elif tag == 'ul':
                # Unordered list
                for li in elem.find_all('li', recursive=False):
                    li_text = get_text_with_inline_formatting(li).strip()
                    parts.append(f"- {li_text}\n")
                parts.append("\n")
            elif tag == 'ol':
                # Ordered list
                index = 1
                for li in elem.find_all('li', recursive=False):
                    li_text = get_text_with_inline_formatting(li).strip()
                    parts.append(f"{index}. {li_text}\n")
                    index += 1
                parts.append("\n")
            elif tag == 'pre':
                # Preformatted block (code or JSON example)
                code_text = elem.get_text()
                # Remove leading newlines for cleanliness
                code_text = code_text.lstrip("\n")
                # Ensure the code block is separated by blank lines
                parts.append("\n")
                parts.append(code_text)
                if not code_text.endswith("\n"):
                    parts.append("\n")
                parts.append("\n")
            elif tag == 'table':
                # Table: convert each row to a text line with columns separated by "|"
                for row in elem.find_all('tr', recursive=False):
                    cells = []
                    for cell in row.find_all(['th', 'td'], recursive=False):
                        cell_text = get_text_with_inline_formatting(cell).strip()
                        cells.append(cell_text)
                    line = " | ".join(cells)
                    parts.append(line + "\n")
                parts.append("\n")
            elif tag.startswith('h') and tag not in ['h1', 'h2', 'h3']:
                # Lower-level heading inside content (e.g., h4)
                head_text = get_text_with_inline_formatting(elem).strip()
                if head_text:
                    parts.append(head_text + "\n\n")
            else:
                # Fallback for other tags (e.g., span, a)
                text = get_text_with_inline_formatting(elem).strip()
                if text:
                    parts.append(text)
    # Join parts and strip trailing whitespace
    content = "".join(parts).strip()
    return content

def split_content_into_chunks(title, content, max_tokens=512, overlap_tokens=50):
    """
    Split a text content into overlapping chunks based on token count.
    Uses a sliding window of size max_tokens with an overlap of overlap_tokens.
    Returns a list of (title, chunk_text) tuples.
    """
    # Find all token positions (split on any whitespace)
    tokens = list(re.finditer(r'\S+', content))
    total_tokens = len(tokens)
    if total_tokens == 0:
        return []
    # If content fits within max_tokens, no splitting needed
    if total_tokens <= max_tokens:
        return [(title, content.strip())]
    chunks = []
    # Adjust window for overlap
    unique_max = max_tokens - overlap_tokens
    start_index = 0
    while start_index < total_tokens:
        if start_index + max_tokens >= total_tokens:
            # Last chunk: take until end of content
            end_index = total_tokens
        else:
            # Take unique_max tokens for this chunk
            end_index = start_index + unique_max
        # Determine substring for this chunk
        start_char = tokens[start_index].start()
        end_char = tokens[end_index - 1].end()
        chunk_text = content[start_char:end_char].strip()
        if chunk_text:
            chunks.append((title, chunk_text))
        # Slide window: move forward and apply overlap
        start_index = end_index
        if start_index < total_tokens:
            start_index = max(0, start_index - overlap_tokens)
    return chunks

def chunk_document(html_content, source=None, max_tokens=512, overlap_tokens=50):
    """
    Parse HTML content and break it into semantic chunks.
    Returns a list of chunk dictionaries.
    """
    soup = BeautifulSoup(html_content, 'lxml')
    # Remove script and style elements
    for tag in soup(['script', 'style']):
        tag.decompose()
    chunks = []
    chunk_id = 1
    # Handle document title (h1) and introduction content before first h2
    doc_title = None
    h1 = soup.find('h1')
    if h1:
        doc_title = h1.get_text().strip()
        first_h2 = soup.find('h2')
        intro_elems = []
        # Collect content after h1 until the first h2 (if any)
        for sib in h1.next_siblings:
            if sib == first_h2:
                break
            if sib.name:
                intro_elems.append(sib)
            else:
                if str(sib).strip():
                    intro_elems.append(sib)
        if intro_elems:
            intro_text = render_elements_to_text(intro_elems)
            if intro_text:
                intro_title = doc_title or "Introduction"
                for title, chunk_text in split_content_into_chunks(intro_title, intro_text, max_tokens, overlap_tokens):
                    chunk_obj = {"id": chunk_id, "title": title, "content": chunk_text}
                    if source:
                        chunk_obj["source"] = source
                    chunks.append(chunk_obj)
                    chunk_id += 1
    # If no h2 sections present, treat entire content (excluding h1) as one chunk
    if not soup.find('h2'):
        if h1 and 'intro_text' in locals():
            # Already handled content after h1
            return chunks
        # Otherwise, take all body content as one section
        body = soup.body if soup.body else soup
        all_elems = []
        for child in body.children:
            if child.name in ['script', 'style', 'h1']:
                continue
            if child.name:
                all_elems.append(child)
            else:
                if str(child).strip():
                    all_elems.append(child)
        text = render_elements_to_text(all_elems)
        if text:
            section_title = doc_title or (source if source else "Document")
            for t, chunk_text in split_content_into_chunks(section_title, text, max_tokens, overlap_tokens):
                chunk_obj = {"id": chunk_id, "title": t, "content": chunk_text}
                if source:
                    chunk_obj["source"] = source
                chunks.append(chunk_obj)
                chunk_id += 1
        return chunks
    # Process each h2 section
    for h2 in soup.find_all('h2'):
        sec_title = h2.get_text().strip()
        section_elems = []
        # Gather content until the next h2
        for sib in h2.next_siblings:
            if sib.name and sib.name.startswith('h2'):
                break
            if sib.name:
                section_elems.append(sib)
            else:
                if str(sib).strip():
                    section_elems.append(sib)
        # Handle subsections (h3) within this section
        current_subtitle = sec_title
        current_elems = []
        for elem in section_elems:
            if hasattr(elem, 'name') and elem.name == 'h3':
                # Finish the current subsection when a new h3 is encountered
                if current_elems:
                    content_text = render_elements_to_text(current_elems)
                    if content_text:
                        combined_title = sec_title if current_subtitle == sec_title else f"{sec_title} - {current_subtitle}"
                        for title, chunk_text in split_content_into_chunks(combined_title, content_text, max_tokens, overlap_tokens):
                            chunk_obj = {"id": chunk_id, "title": title, "content": chunk_text}
                            if source:
                                chunk_obj["source"] = source
                            chunks.append(chunk_obj)
                            chunk_id += 1
                # Start a new subsection
                current_subtitle = elem.get_text().strip()
                current_elems = []
            else:
                current_elems.append(elem)
        # Finalize the last subsection in this section
        if current_elems:
            content_text = render_elements_to_text(current_elems)
            if content_text:
                combined_title = sec_title if current_subtitle == sec_title else f"{sec_title} - {current_subtitle}"
                for title, chunk_text in split_content_into_chunks(combined_title, content_text, max_tokens, overlap_tokens):
                    chunk_obj = {"id": chunk_id, "title": title, "content": chunk_text}
                    if source:
                        chunk_obj["source"] = source
                    chunks.append(chunk_obj)
                    chunk_id += 1
    return chunks

def main():
    parser = argparse.ArgumentParser(description="Semantic chunking of API documentation HTML.")
    parser.add_argument("input", help="Path to input HTML file (or '-' to read from stdin).")
    parser.add_argument("-o", "--output", help="Path to output JSON file. If not provided, prints to stdout.")
    parser.add_argument("--source", help="Optional source tag to label the chunks (e.g. 'Transaction API').")
    parser.add_argument("--max_tokens", type=int, default=512, help="Maximum tokens per chunk. Default=512.")
    parser.add_argument("--overlap_tokens", type=int, default=50, help="Number of overlapping tokens between chunks. Default=50.")
    args = parser.parse_args()
    # Read input HTML
    if args.input == "-":
        html_content = sys.stdin.read()
    else:
        with open(args.input, 'r', encoding='utf-8') as f:
            html_content = f.read()
    # Generate chunks
    chunks = chunk_document(html_content, source=args.source, max_tokens=args.max_tokens, overlap_tokens=args.overlap_tokens)
    # Output JSON
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)
    else:
        print(json.dumps(chunks, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
