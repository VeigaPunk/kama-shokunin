#!/usr/bin/env python3
"""render-check.py - does the same text render as a table? (markdown-it-py, js-default, html on).

Proves the A1/A2/A4b/A6/A14 claims: which of the attacked Markdown forms reach an operator as a
table. Requires markdown-it-py (installed on this host as `markdown-it` 4.2.0).
"""
from markdown_it import MarkdownIt

MD = MarkdownIt("js-default", {"html": True})
CASES = {
    "A1-html-comment": "Intro.\n\n<!--\n| a | b |\n|---|---|\n| `x` | `y` |\n-->\n\nAfter.\n",
    "A2-setext": "Probe reason codes\n------------------\n\n| a | b |\n|---|---|\n| `x` | `y` |\n",
    "A4-tab-indent": "| a | b |\n|---|---|\n\t| `x` | `y` |\n",
    "A4b-two-space-indent": "| a | b |\n|---|---|\n  | `x` | `y` |\n",
    "A6-escaped-pipe": "| a | b |\n|---|---|\n| `x` | left \\| right |\n",
    "A14-blockquote": "> | a | b |\n> |---|---|\n> | `x` | `y` |\n",
}
for name, src in CASES.items():
    html = MD.render(src)
    tbody = html.split("<tbody>", 1)[1].split("</tbody>", 1)[0] if "<tbody>" in html else ""
    print(f"{name:22s} tables={html.count('<table>')} tbody_rows={tbody.count('<tr>')} "
          f"code_blocks={html.count('<pre>')} h2={html.count('<h2>')} "
          f"literal_pipe={'left | right' in html}")
