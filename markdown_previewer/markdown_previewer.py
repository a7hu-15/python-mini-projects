"""
Markdown Live Previewer & Parser
---------------------------------
A Python utility to parse Markdown text into ANSI-formatted terminal text or export to clean HTML.
"""

import sys
import re
import html
from typing import List

class MarkdownPreviewer:
    """Parses standard Markdown syntax to ANSI formatted strings or HTML output."""
    
    def __init__(self, raw_text: str):
        self.raw_text = raw_text

    def to_ansi(self) -> str:
        """Converts Markdown text to ANSI color-coded terminal text."""
        lines = self.raw_text.split('\n')
        formatted_lines: List[str] = []
        in_code_block = False

        for line in lines:
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                formatted_lines.append("\033[90m----------------------------------------\033[0m")
                continue
            
            if in_code_block:
                formatted_lines.append(f"\033[36m    {line}\033[0m")
                continue

            # Headers
            if line.startswith('# '):
                formatted_lines.append(f"\033[1;35m# {line[2:]}\033[0m")
            elif line.startswith('## '):
                formatted_lines.append(f"\033[1;34m## {line[3:]}\033[0m")
            elif line.startswith('### '):
                formatted_lines.append(f"\033[1;33m### {line[4:]}\033[0m")
            # Unordered lists
            elif line.strip().startswith('- ') or line.strip().startswith('* '):
                formatted_lines.append(f"  \033[32m•\033[0m {line.strip()[2:]}")
            # Blockquotes
            elif line.startswith('> '):
                formatted_lines.append(f"\033[37;40m│ {line[2:]}\033[0m")
            else:
                # Bold & Italic inline formatting
                text = re.sub(r'\*\*(.*?)\*\*', r'\033[1m\1\033[0m', line)
                text = re.sub(r'\*(.*?)\*', r'\033[3m\1\033[0m', text)
                formatted_lines.append(text)

        return '\n'.join(formatted_lines)

    def to_html(self) -> str:
        """Converts Markdown text to styled HTML document."""
        escaped_text = html.escape(self.raw_text)
        body_lines = []
        for line in escaped_text.split('\n'):
            if line.startswith('# '):
                body_lines.append(f"<h1>{line[2:]}</h1>")
            elif line.startswith('## '):
                body_lines.append(f"<h2>{line[3:]}</h2>")
            elif line.startswith('### '):
                body_lines.append(f"<h3>{line[4:]}</h3>")
            elif line.startswith('- ') or line.startswith('* '):
                body_lines.append(f"<li>{line[2:]}</li>")
            else:
                body_lines.append(f"<p>{line}</p>")

        return (
            "<!DOCTYPE html>\n<html>\n<head>\n"
            "<meta charset='utf-8'><title>Markdown Preview</title>\n"
            "<style>body { font-family: system-ui, sans-serif; max-width: 800px; margin: 2rem auto; padding: 0 1rem; line-height: 1.6; color: #222; }</style>\n"
            "</head>\n<body>\n" + '\n'.join(body_lines) + "\n</body>\n</html>"
        )


def main():
    sample_md = """# Markdown Live Previewer
## Features
- Terminal ANSI formatting
- HTML Export capability
- Support for **bold** and *italic* text

```python
print("Hello, Markdown!")
```
"""
    previewer = MarkdownPreviewer(sample_md)
    print("=== Terminal Preview ===")
    print(previewer.to_ansi())
    print("\n=== Generated HTML ===")
    print(previewer.to_html()[:250] + "...\n")

if __name__ == '__main__':
    main()
