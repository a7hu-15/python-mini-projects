"""
📝 Markdown to HTML Converter

A lightweight Markdown-to-HTML converter built from scratch using regex.
Supports the most common Markdown elements without any external dependencies.

Supported syntax:
    - Headers (# h1 through ###### h6)
    - Bold (**text** or __text__)
    - Italic (*text* or _text_)
    - Bold + Italic (***text***)
    - Inline code (`code`)
    - Code blocks (``` ... ```)
    - Links ([text](url))
    - Images (![alt](url))
    - Unordered lists (- item or * item)
    - Ordered lists (1. item)
    - Blockquotes (> text)
    - Horizontal rules (--- or ***)
    - Paragraphs (automatic)

Usage:
    python md_to_html.py                     # Interactive mode
    python md_to_html.py input.md            # Convert file
    python md_to_html.py input.md output.html  # Convert and save

>>> convert_line("# Hello World")
'<h1>Hello World</h1>'

>>> convert_line("**bold text**")
'<strong>bold text</strong>'

>>> convert_line("*italic text*")
'<em>italic text</em>'

>>> convert_line("`inline code`")
'<code>inline code</code>'

>>> convert_line("[Google](https://google.com)")
'<a href="https://google.com">Google</a>'
"""

from __future__ import annotations

import re
import sys


def convert_line(line: str) -> str:
    """
    Convert a single line of Markdown to HTML.

    Handles inline elements: bold, italic, code, links, images.

    Args:
        line: A single line of Markdown text.

    Returns:
        The line converted to HTML.

    >>> convert_line("## Section Title")
    '<h2>Section Title</h2>'

    >>> convert_line("Normal paragraph text")
    'Normal paragraph text'

    >>> convert_line("***bold and italic***")
    '<strong><em>bold and italic</em></strong>'

    >>> convert_line("![Logo](logo.png)")
    '<img src="logo.png" alt="Logo">'

    >>> convert_line("---")
    '<hr>'
    """
    # Horizontal rule (must check before list items)
    if re.match(r"^(\-{3,}|\*{3,}|_{3,})$", line.strip()):
        return "<hr>"

    # Headers (h1 - h6)
    header_match = re.match(r"^(#{1,6})\s+(.+)$", line)
    if header_match:
        level = len(header_match.group(1))
        content = header_match.group(2)
        content = _apply_inline_formatting(content)
        return f"<h{level}>{content}</h{level}>"

    # Apply inline formatting to regular lines
    line = _apply_inline_formatting(line)

    return line


def _apply_inline_formatting(text: str) -> str:
    """
    Apply inline Markdown formatting (bold, italic, code, links, images).

    Args:
        text: Text to format.

    Returns:
        Text with inline HTML formatting applied.

    >>> _apply_inline_formatting("**bold** and *italic*")
    '<strong>bold</strong> and <em>italic</em>'

    >>> _apply_inline_formatting("Use `print()` function")
    'Use <code>print()</code> function'
    """
    # Inline code (must be first to prevent other formatting inside code)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)

    # Images: ![alt](url)
    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r'<img src="\2" alt="\1">', text)

    # Links: [text](url)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)

    # Bold + Italic: ***text*** or ___text___
    text = re.sub(r"\*{3}(.+?)\*{3}", r"<strong><em>\1</em></strong>", text)
    text = re.sub(r"_{3}(.+?)_{3}", r"<strong><em>\1</em></strong>", text)

    # Bold: **text** or __text__
    text = re.sub(r"\*{2}(.+?)\*{2}", r"<strong>\1</strong>", text)
    text = re.sub(r"_{2}(.+?)_{2}", r"<strong>\1</strong>", text)

    # Italic: *text* or _text_
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    text = re.sub(r"(?<!\w)_(.+?)_(?!\w)", r"<em>\1</em>", text)

    return text


def markdown_to_html(markdown_text: str) -> str:
    """
    Convert a full Markdown document to HTML.

    Handles block-level elements (code blocks, lists, blockquotes, paragraphs)
    in addition to inline formatting.

    Args:
        markdown_text: Full Markdown text to convert.

    Returns:
        Complete HTML string.

    >>> print(markdown_to_html("# Title\\n\\nHello world"))
    <h1>Title</h1>
    <p>Hello world</p>

    >>> print(markdown_to_html("- item1\\n- item2"))
    <ul>
    <li>item1</li>
    <li>item2</li>
    </ul>

    >>> print(markdown_to_html("> A quote"))
    <blockquote>
    <p>A quote</p>
    </blockquote>
    """
    lines = markdown_text.split("\n")
    html_lines = []
    i = 0
    in_code_block = False
    code_language = ""
    code_lines = []

    while i < len(lines):
        line = lines[i]

        # Code blocks (```)
        if line.strip().startswith("```"):
            if not in_code_block:
                in_code_block = True
                code_language = line.strip()[3:].strip()
                code_lines = []
            else:
                in_code_block = False
                lang_attr = f' class="language-{code_language}"' if code_language else ""
                code_content = "\n".join(code_lines)
                html_lines.append(f"<pre><code{lang_attr}>{code_content}</code></pre>")
            i += 1
            continue

        if in_code_block:
            # Escape HTML inside code blocks
            escaped = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            code_lines.append(escaped)
            i += 1
            continue

        # Empty line
        if line.strip() == "":
            i += 1
            continue

        # Blockquotes
        if line.strip().startswith(">"):
            quote_lines = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                content = re.sub(r"^>\s?", "", lines[i])
                quote_lines.append(content)
                i += 1
            inner_html = markdown_to_html("\n".join(quote_lines))
            html_lines.append(f"<blockquote>\n{inner_html}\n</blockquote>")
            continue

        # Unordered lists (- or *)
        if re.match(r"^\s*[-*]\s+", line):
            list_items = []
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
                content = re.sub(r"^\s*[-*]\s+", "", lines[i])
                content = _apply_inline_formatting(content)
                list_items.append(f"<li>{content}</li>")
                i += 1
            html_lines.append("<ul>\n" + "\n".join(list_items) + "\n</ul>")
            continue

        # Ordered lists (1. 2. 3.)
        if re.match(r"^\s*\d+\.\s+", line):
            list_items = []
            while i < len(lines) and re.match(r"^\s*\d+\.\s+", lines[i]):
                content = re.sub(r"^\s*\d+\.\s+", "", lines[i])
                content = _apply_inline_formatting(content)
                list_items.append(f"<li>{content}</li>")
                i += 1
            html_lines.append("<ol>\n" + "\n".join(list_items) + "\n</ol>")
            continue

        # Regular line — convert and wrap in <p>
        converted = convert_line(line)
        if not converted.startswith("<h") and not converted.startswith("<hr"):
            converted = f"<p>{converted}</p>"
        html_lines.append(converted)
        i += 1

    return "\n".join(html_lines)


def wrap_in_html_document(body_html: str, title: str = "Converted Document") -> str:
    """
    Wrap HTML body content in a complete HTML5 document with basic styling.

    Args:
        body_html: The HTML body content.
        title: The document title.

    Returns:
        A complete HTML document string.
    """
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 2rem auto;
            padding: 0 1rem;
            line-height: 1.6;
            color: #333;
            background: #fafafa;
        }}
        pre {{
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 1rem;
            border-radius: 6px;
            overflow-x: auto;
        }}
        code {{
            background: #e8e8e8;
            padding: 0.2em 0.4em;
            border-radius: 3px;
            font-size: 0.9em;
        }}
        pre code {{
            background: none;
            padding: 0;
        }}
        blockquote {{
            border-left: 4px solid #ddd;
            margin: 1rem 0;
            padding: 0.5rem 1rem;
            color: #666;
            background: #f9f9f9;
        }}
        hr {{
            border: none;
            border-top: 2px solid #eee;
            margin: 2rem 0;
        }}
        img {{
            max-width: 100%;
            height: auto;
        }}
        a {{
            color: #0366d6;
        }}
    </style>
</head>
<body>
{body_html}
</body>
</html>"""


if __name__ == "__main__":
    import doctest

    doctest.testmod()

    if len(sys.argv) > 1:
        # File mode
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None

        with open(input_file, "r", encoding="utf-8") as f:
            md_content = f.read()

        html = markdown_to_html(md_content)
        full_html = wrap_in_html_document(html, title=input_file)

        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(full_html)
            print(f"✅ Converted '{input_file}' → '{output_file}'")
        else:
            print(full_html)
    else:
        # Interactive demo
        sample_md = """# Markdown to HTML Converter

This is a **bold** statement and this is *italic*.

## Features

- Supports **headers** (h1-h6)
- Supports *inline* formatting
- Supports `inline code`
- Supports [links](https://example.com)

### Code Example

```python
def hello():
    print("Hello, World!")
```

> This is a blockquote.
> It can span multiple lines.

---

1. First item
2. Second item
3. Third item

That's ***all*** folks!
"""
        print("📝 Markdown to HTML Converter — Demo\n")
        print("Input Markdown:")
        print("-" * 40)
        print(sample_md)
        print("-" * 40)
        print("\nOutput HTML:")
        print("-" * 40)
        print(markdown_to_html(sample_md))
